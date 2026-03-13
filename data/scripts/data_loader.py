"""
GTFS data loading and service-date filtering utilities.
"""

from __future__ import annotations

import os
from typing import Set

import numpy as np
import pandas as pd

from config import RAW_DATA_DIR, RAIL_ROUTE_TYPES


# ── Low-level helpers ────────────────────────────────────────────────

def gtfs_time_to_minutes(value) -> float:
    """Convert a GTFS time string (HH:MM:SS, may exceed 24 h) to minutes."""
    if pd.isna(value):
        return np.nan
    h, m, s = map(int, str(value).split(":"))
    return h * 60 + m + s / 60.0


def derive_station_key(df: pd.DataFrame) -> pd.Series:
    """Return a canonical station key: *parent_station* if set, else *stop_id*."""
    parent = df["parent_station"].fillna("").astype(str).str.strip()
    return parent.where(parent.ne(""), df["stop_id"].astype(str))


# ── File readers ─────────────────────────────────────────────────────

def load_stops(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    """Load ``stops.txt`` with proper dtypes."""
    return pd.read_csv(
        os.path.join(data_dir, "stops.txt"),
        dtype={5: str, 6: str},
        low_memory=False,
    )


def load_routes(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(data_dir, "routes.txt"),
        usecols=["route_id", "route_type", "route_short_name", "route_desc"],
        low_memory=False,
    )
    df["route_type"] = pd.to_numeric(df["route_type"], errors="coerce")
    return df


def load_trips(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(data_dir, "trips.txt"),
        usecols=["trip_id", "route_id", "service_id", "trip_short_name", "trip_headsign"],
        low_memory=False,
    )


def load_calendar(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(data_dir, "calendar.txt"), low_memory=False)
    weekday_cols = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for c in weekday_cols:
        df[c] = df[c].astype(int)
    df[["start_date", "end_date"]] = df[["start_date", "end_date"]].astype(int)
    return df


def load_calendar_dates(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(data_dir, "calendar_dates.txt"),
        usecols=["service_id", "date", "exception_type"],
        low_memory=False,
    )
    df[["date", "exception_type"]] = df[["date", "exception_type"]].astype(int)
    return df


def load_stop_times_basic(data_dir: str = RAW_DATA_DIR) -> pd.DataFrame:
    """Load ``stop_times.txt`` with only trip_id and stop_id (lightweight)."""
    return pd.read_csv(
        os.path.join(data_dir, "stop_times.txt"),
        usecols=["trip_id", "stop_id"],
    )


def load_stop_times_hourly(
    data_dir: str = RAW_DATA_DIR,
    trip_ids: Set[str] | None = None,
    stop_ids: Set[str] | None = None,
    chunksize: int = 1_000_000,
) -> pd.DataFrame:
    """Load stop_times with departure minutes parsed, optionally filtered in chunks."""
    usecols = ["trip_id", "stop_id", "departure_time"]
    dtype = {"trip_id": str, "stop_id": str, "departure_time": str}

    if trip_ids is None and stop_ids is None:
        df = pd.read_csv(
            os.path.join(data_dir, "stop_times.txt"),
            usecols=usecols,
            dtype=dtype,
        )
    else:
        trip_ids = {str(t) for t in trip_ids} if trip_ids is not None else None
        stop_ids = {str(s) for s in stop_ids} if stop_ids is not None else None

        parts = []
        for chunk in pd.read_csv(
            os.path.join(data_dir, "stop_times.txt"),
            usecols=usecols,
            dtype=dtype,
            chunksize=chunksize,
        ):
            mask = pd.Series(True, index=chunk.index)
            if trip_ids is not None:
                mask &= chunk["trip_id"].isin(trip_ids)
            if stop_ids is not None:
                mask &= chunk["stop_id"].isin(stop_ids)
            filtered = chunk.loc[mask]
            if not filtered.empty:
                parts.append(filtered)

        if parts:
            df = pd.concat(parts, ignore_index=True)
        else:
            df = pd.DataFrame(columns=usecols)

    df["departure_minutes"] = df["departure_time"].map(gtfs_time_to_minutes)
    df["hour"] = np.floor(df["departure_minutes"] / 60).fillna(-1).astype(int)
    return df


# ── Service-date logic ───────────────────────────────────────────────

def services_active_on_date(
    calendar_df: pd.DataFrame,
    calendar_dates_df: pd.DataFrame,
    service_date: pd.Timestamp,
) -> Set:
    """Return the set of *service_id* values active on *service_date*."""
    yyyymmdd = int(service_date.strftime("%Y%m%d"))
    weekday = service_date.day_name().lower()
    active: Set = set(
        calendar_df.loc[
            (calendar_df[weekday] == 1)
            & (calendar_df["start_date"] <= yyyymmdd)
            & (calendar_df["end_date"] >= yyyymmdd),
            "service_id",
        ]
    )
    for _, row in calendar_dates_df[calendar_dates_df["date"] == yyyymmdd].iterrows():
        if row["exception_type"] == 1:
            active.add(row["service_id"])
        elif row["exception_type"] == 2:
            active.discard(row["service_id"])
    return active


# ── Rail-specific filtering ──────────────────────────────────────────

def filter_rail_routes(routes_df: pd.DataFrame) -> pd.DataFrame:
    return routes_df[routes_df["route_type"].isin(RAIL_ROUTE_TYPES)]


def filter_rail_trips(trips_df: pd.DataFrame, rail_routes_df: pd.DataFrame) -> pd.DataFrame:
    return trips_df[trips_df["route_id"].isin(rail_routes_df["route_id"])]


def filter_rail_stop_ids(
    stop_times_df: pd.DataFrame,
    rail_trips_df: pd.DataFrame,
) -> np.ndarray:
    """Return unique stop_id values served by rail trips."""
    return stop_times_df[
        stop_times_df["trip_id"].isin(rail_trips_df["trip_id"])
    ]["stop_id"].unique()


def build_station_meta(stops_df: pd.DataFrame) -> pd.DataFrame:
    """Build a de-duplicated station-level metadata table."""
    en = stops_df.copy()
    en["station_key"] = derive_station_key(en)
    en["is_canonical"] = en["stop_id"].astype(str).eq(en["station_key"])
    return (
        en.sort_values(["is_canonical", "stop_name"], ascending=[False, True])
        .drop_duplicates("station_key")[["station_key", "stop_name", "stop_lat", "stop_lon"]]
        .rename(columns={"stop_name": "station_name"})
        .reset_index(drop=True)
    )
