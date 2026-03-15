"""
Rail reachability engine: builds a time-expanded graph from GTFS data
and runs a modified Dijkstra to compute earliest arrivals.
"""

from __future__ import annotations

import heapq
import os
from bisect import bisect_left
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Set, Tuple

import numpy as np
import pandas as pd

from config import (
    MIN_TRANSFER_MINUTES,
    RAW_DATA_DIR,
    STOP_TIMES_CHUNK_SIZE,
)
from data_loader import (
    build_station_meta,
    derive_station_key,
    gtfs_time_to_minutes,
    services_active_on_date,
)


# ── Type aliases ─────────────────────────────────────────────────────

TripInstanceId = Tuple[str, int]  # (trip_id, day_offset)


# ── Graph construction ───────────────────────────────────────────────

def compute_active_services(
    calendar_df: pd.DataFrame,
    calendar_dates_df: pd.DataFrame,
    analysis_date: pd.Timestamp,
    max_elapsed_minutes: int,
) -> pd.DataFrame:
    """
    Return a DataFrame of ``(service_id, day_offset)`` pairs active within
    the analysis window starting at *analysis_date*.
    """
    service_day_span = max(1, int(np.ceil((23 * 60 + 45 + max_elapsed_minutes) / (24 * 60))))
    rows = []
    for d in range(service_day_span):
        for sid in services_active_on_date(
            calendar_df, calendar_dates_df, analysis_date + pd.Timedelta(days=d)
        ):
            rows.append({"service_id": sid, "day_offset": d})
    return pd.DataFrame(rows).drop_duplicates()


def compute_active_rail_trips(
    rail_trips_df: pd.DataFrame,
    active_offsets: pd.DataFrame,
) -> pd.DataFrame:
    return rail_trips_df.merge(active_offsets, on="service_id", how="inner")


def load_active_stop_times(
    active_trip_ids: Set[str],
    swiss_train_stop_ids: Set[str],
    stops_all_df: pd.DataFrame,
    active_rail_df: pd.DataFrame,
    data_dir: str = RAW_DATA_DIR,
) -> pd.DataFrame:
    """
    Stream ``stop_times.txt`` in chunks, keep only rows for active rail trips
    and Swiss train stops, then enrich with station keys and absolute times.
    """
    stop_times_cols = ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"]

    st_all_keys = stops_all_df[["stop_id", "station_key"]].copy()

    parts: List[pd.DataFrame] = []
    for chunk in pd.read_csv(
        os.path.join(data_dir, "stop_times.txt"),
        usecols=stop_times_cols,
        dtype={"trip_id": str, "arrival_time": str, "departure_time": str, "stop_id": str},
        chunksize=STOP_TIMES_CHUNK_SIZE,
    ):
        filtered = chunk[
            chunk["trip_id"].isin(active_trip_ids) & chunk["stop_id"].isin(swiss_train_stop_ids)
        ]
        if not filtered.empty:
            parts.append(filtered)

    if not parts:
        return pd.DataFrame(columns=stop_times_cols)

    active_st = pd.concat(parts, ignore_index=True)
    active_st["stop_sequence"] = pd.to_numeric(active_st["stop_sequence"], errors="coerce")
    active_st = active_st.merge(st_all_keys, on="stop_id", how="left")

    merge_cols = ["trip_id", "day_offset", "trip_short_name", "route_short_name", "route_desc", "trip_headsign"]
    available_cols = [c for c in merge_cols if c in active_rail_df.columns]
    active_st = active_st.merge(active_rail_df[available_cols], on="trip_id", how="inner")

    active_st["arrival_minutes"] = active_st["arrival_time"].map(gtfs_time_to_minutes)
    active_st["departure_minutes"] = active_st["departure_time"].map(gtfs_time_to_minutes)
    active_st["arrival_abs"] = active_st["arrival_minutes"] + active_st["day_offset"] * 24 * 60
    active_st["departure_abs"] = active_st["departure_minutes"] + active_st["day_offset"] * 24 * 60
    active_st = active_st.sort_values(["trip_id", "day_offset", "stop_sequence"]).reset_index(drop=True)
    return active_st


def build_trip_graph(active_st: pd.DataFrame):
    """
    Build the time-expanded trip graph.

    Returns
    -------
    trip_instances : dict mapping TripInstanceId → {label, stops}
    departures_by_station : dict mapping station_key → sorted list of
        (departure_abs, instance_id, stop_index)
    departure_times_by_station : dict mapping station_key → sorted departure times
    """
    trip_instances: Dict[TripInstanceId, dict] = {}
    departures_by_station: Dict[str, List] = defaultdict(list)

    for (tid, do), grp in active_st.groupby(["trip_id", "day_offset"], sort=False):
        rows = []
        for r in grp.itertuples(index=False):
            sk = getattr(r, "station_key", None)
            if pd.isna(sk):
                continue
            rows.append({"station_key": sk, "arrival": r.arrival_abs, "departure": r.departure_abs})

        if len(rows) < 2:
            continue

        # Collapse consecutive duplicate stations
        compressed: List[dict] = []
        for s in rows:
            if compressed and compressed[-1]["station_key"] == s["station_key"]:
                if pd.notna(s["arrival"]) and (
                    pd.isna(compressed[-1]["arrival"]) or s["arrival"] < compressed[-1]["arrival"]
                ):
                    compressed[-1]["arrival"] = s["arrival"]
                if pd.notna(s["departure"]):
                    compressed[-1]["departure"] = s["departure"]
                continue
            compressed.append(s)

        if len(compressed) < 2:
            continue

        h = grp.iloc[0]
        label = next(
            (
                v
                for v in [
                    getattr(h, "trip_short_name", None),
                    getattr(h, "route_short_name", None),
                    getattr(h, "trip_headsign", None),
                    tid,
                ]
                if pd.notna(v) and str(v).strip()
            ),
            tid,
        )

        iid: TripInstanceId = (tid, int(do))
        trip_instances[iid] = {"label": label, "stops": compressed}

        for i, s in enumerate(compressed[:-1]):
            has_later_stop = any(
                c["station_key"] != s["station_key"] and pd.notna(c["arrival"])
                for c in compressed[i + 1 :]
            )
            if pd.notna(s["departure"]) and has_later_stop:
                departures_by_station[s["station_key"]].append((float(s["departure"]), iid, i))

    for k in departures_by_station:
        departures_by_station[k].sort(key=lambda x: x[0])

    departure_times_by_station = {k: [x[0] for x in v] for k, v in departures_by_station.items()}

    return trip_instances, departures_by_station, departure_times_by_station


# ── Dijkstra ─────────────────────────────────────────────────────────

def compute_earliest_arrivals(
    start_station_key: str,
    dep_min: int,
    horizon_minutes: int,
    trip_instances: dict,
    departures_by_station: dict,
    departure_times_by_station: dict,
) -> Dict[str, float]:
    """
    Modified Dijkstra on the time-expanded rail graph.

    Returns a dict mapping *station_key* → earliest absolute arrival time (minutes).
    """
    dep_min, horizon_minutes = int(dep_min), int(horizon_minutes)
    limit = dep_min + horizon_minutes

    best: Dict[str, float] = {start_station_key: float(dep_min)}
    pq: list = [(float(dep_min), start_station_key)]

    while pq:
        arr, sk = heapq.heappop(pq)
        if arr > best.get(sk, np.inf):
            continue

        ready = arr if sk == start_station_key else arr + MIN_TRANSFER_MINUTES
        times = departure_times_by_station.get(sk, [])
        deps = departures_by_station.get(sk, [])
        idx = bisect_left(times, ready)

        for dt, iid, si in deps[idx:]:
            if dt > limit:
                break
            for ds in trip_instances[iid]["stops"][si + 1 :]:
                a = ds["arrival"]
                if pd.isna(a) or a > limit:
                    continue
                dsk = ds["station_key"]
                if a < best.get(dsk, np.inf):
                    best[dsk] = float(a)
                    heapq.heappush(pq, (float(a), dsk))

    return best


# ── High-level API ───────────────────────────────────────────────────

class ReachabilityEngine:
    """
    Stateful wrapper that caches the trip graph and exposes a
    ``build_reachable_frame`` method with LRU caching.
    """

    def __init__(
        self,
        swiss_train_meta: pd.DataFrame,
        trip_instances: dict,
        departures_by_station: dict,
        departure_times_by_station: dict,
        start_station_key: str,
    ):
        self.swiss_train_meta = swiss_train_meta
        self.trip_instances = trip_instances
        self.departures_by_station = departures_by_station
        self.departure_times_by_station = departure_times_by_station
        self.start_station_key = start_station_key

    @lru_cache(maxsize=256)
    def build_reachable_frame(
        self, departure_minutes: int, horizon_minutes: int
    ) -> pd.DataFrame:
        dep_min = int(departure_minutes)
        h = int(horizon_minutes)
        arrivals = compute_earliest_arrivals(
            self.start_station_key,
            dep_min,
            h,
            self.trip_instances,
            self.departures_by_station,
            self.departure_times_by_station,
        )
        rf = self.swiss_train_meta.copy()
        rf["arrival_minutes"] = rf["station_key"].map(arrivals)
        rf["reachable"] = rf["arrival_minutes"].notna()
        rf["travel_minutes"] = rf["arrival_minutes"] - dep_min
        rf.loc[~rf["reachable"], "travel_minutes"] = np.nan
        return rf


def resolve_start_station(
    swiss_train_meta: pd.DataFrame,
    all_stops_meta: pd.DataFrame,
    station_name: str,
) -> Tuple[str, pd.Series]:
    """
    Look up *station_name* in the rail meta table (fallback: all stops).

    Returns
    -------
    station_key : str
    station_row : pd.Series
    """
    candidates = swiss_train_meta[
        swiss_train_meta["station_name"].str.casefold() == station_name.casefold()
    ]
    if candidates.empty:
        candidates = all_stops_meta[
            all_stops_meta["station_name"].str.casefold() == station_name.casefold()
        ]
    if candidates.empty:
        raise ValueError(f"Station not found: {station_name}")

    key = candidates.iloc[0]["station_key"]
    row = swiss_train_meta[swiss_train_meta["station_key"] == key].iloc[0]
    return key, row
