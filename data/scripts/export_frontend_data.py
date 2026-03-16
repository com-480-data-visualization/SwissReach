"""
Minimal frontend data export — pandas + networkx only, no geopandas/matplotlib.

Usage:
    python3 data/scripts/export_frontend_data.py

Outputs to docs/public/data/:
    stations.json
    reachability_{origin}_{HHMM}.json  (4 origins × 4 departure times = 16 files)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Make sibling modules importable when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from config import ANALYSIS_DATE, RAW_DATA_DIR
from data_loader import (
    build_station_meta,
    filter_rail_routes,
    filter_rail_stop_ids,
    filter_rail_trips,
    load_calendar,
    load_calendar_dates,
    load_routes,
    load_stop_times_basic,
    load_stop_times_hourly,
    load_stops,
    load_trips,
)
from reachability import (
    ReachabilityEngine,
    build_trip_graph,
    compute_active_rail_trips,
    compute_active_services,
    load_active_stop_times,
    resolve_start_station,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "docs" / "public" / "data"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load GTFS ────────────────────────────────────────────────────
    print("Loading GTFS…")
    stops_df       = load_stops()
    routes_df      = load_routes()
    trips_df       = load_trips()
    calendar_df    = load_calendar()
    cal_dates_df   = load_calendar_dates()
    stop_times_raw = load_stop_times_basic()

    # ── Rail stations (no spatial filter — GTFS is already Swiss) ────
    rail_routes = filter_rail_routes(routes_df)
    rail_trips  = filter_rail_trips(trips_df, rail_routes)
    rail_stop_ids = filter_rail_stop_ids(stop_times_raw, rail_trips)

    # Keep only rail stops inside Switzerland's bounding box, then dedup
    # (Swiss GTFS includes cross-border trains to Germany, France, Netherlands, etc.)
    CH_LAT = (45.80, 47.85)
    CH_LON = (5.90, 10.55)
    train_stops = stops_df[
        stops_df["stop_id"].astype(str).isin([str(s) for s in rail_stop_ids])
        & stops_df["stop_lat"].between(*CH_LAT)
        & stops_df["stop_lon"].between(*CH_LON)
    ].copy()
    swiss_train_meta = build_station_meta(train_stops)
    print(f"  {len(swiss_train_meta)} rail stations (inside Switzerland)")

    # ── Build reachability graph ──────────────────────────────────────
    print("Building reachability graph…")
    active_services = compute_active_services(
        calendar_df, cal_dates_df, ANALYSIS_DATE, max_elapsed_minutes=48 * 60
    )
    active_rail = compute_active_rail_trips(rail_trips, active_services)
    active_trip_ids     = set(active_rail["trip_id"].astype(str))
    swiss_stop_id_strs  = set(train_stops["stop_id"].astype(str))

    stop_times_w = load_stop_times_hourly(
        data_dir=RAW_DATA_DIR,
        trip_ids=active_trip_ids,
        stop_ids=swiss_stop_id_strs,
    )
    stops_keyed = stops_df.copy()
    stops_keyed["stop_id"]      = stops_keyed["stop_id"].astype(str)
    stops_keyed["station_key"]  = stops_keyed["parent_station"].fillna("").astype(str).str.strip()
    stops_keyed["station_key"]  = stops_keyed["station_key"].where(
        stops_keyed["station_key"].ne(""), stops_keyed["stop_id"]
    )
    stops_with_keys = train_stops[["stop_id"]].copy()
    stops_with_keys["stop_id"] = stops_with_keys["stop_id"].astype(str)
    stops_with_keys = stops_with_keys.merge(
        stops_keyed[["stop_id", "station_key"]], on="stop_id", how="left"
    ).drop_duplicates("stop_id")

    station_windowed = (
        stop_times_w
        .merge(stops_with_keys, on="stop_id", how="left")
        .dropna(subset=["station_key"])
    )
    active_st = load_active_stop_times(
        active_trip_ids, swiss_stop_id_strs, stops_keyed, active_rail
    )
    trip_instances, departures_by_station, departure_times_by_station = build_trip_graph(active_st)

    # ── Export JSON files ─────────────────────────────────────────────
    print("Exporting JSON…")
    # stations index (lat/lon for all stations)
    idx = swiss_train_meta[["station_key", "station_name", "stop_lat", "stop_lon"]].copy()
    idx = idx.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})
    idx.to_json(DATA_DIR / "stations.json", orient="records", indent=2)
    print(f"  stations.json ({len(idx)} stations)")

    origins    = ["Lausanne", "Bern", "Genève", "Zürich HB"]
    departures = [6 * 60, 8 * 60, 12 * 60, 18 * 60]

    for origin in origins:
        slug = origin.lower().replace(" ", "_").replace("ü", "u").replace("è", "e")
        start_key, _ = resolve_start_station(swiss_train_meta, swiss_train_meta, origin)
        engine = ReachabilityEngine(
            swiss_train_meta,
            trip_instances,
            departures_by_station,
            departure_times_by_station,
            start_key,
        )
        for dep in departures:
            rf  = engine.build_reachable_frame(dep, 6 * 60)
            out = rf[["station_key", "station_name", "stop_lat", "stop_lon", "travel_minutes"]].copy()
            out = out.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})
            out["travel_minutes"] = out["travel_minutes"].where(out["travel_minutes"].notna(), other=None)
            fname = f"reachability_{slug}_{dep // 60:02d}{dep % 60:02d}.json"
            out.to_json(DATA_DIR / fname, orient="records", indent=2)
            print(f"  {fname}  ({int(rf['reachable'].sum())} reachable)")

    print(f"\nDone → {DATA_DIR}")


if __name__ == "__main__":
    main()
