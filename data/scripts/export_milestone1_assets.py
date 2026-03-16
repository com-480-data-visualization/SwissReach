"""
Export static figures and summary tables for Milestone 1 docs/reporting.

Usage:
    python3 data/scripts/export_milestone1_assets.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

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
from spatial import filter_rail_stations, filter_stops_within_switzerland, load_swiss_boundary
from visualization import (
    apply_mpl_defaults,
    plot_busiest_stops,
    plot_rail_stations_map,
    plot_reachability_comparison_heatmap,
    plot_reachability_map,
    plot_station_meta_map,
    plot_stops_map,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_PUBLIC_DIR = PROJECT_ROOT / "docs" / "public"
FIGURES_DIR = DOCS_PUBLIC_DIR / "figures"
DATA_DIR = DOCS_PUBLIC_DIR / "data"


def export_static_maps(
    stops_inside,
    swiss_boundary_proj,
    train_stations_df,
    train_stations_dedup,
) -> None:
    plot_stops_map(
        stops_inside,
        swiss_boundary_proj,
        output_path=str(FIGURES_DIR / "swiss_public_transport_stops.png"),
        show=False,
    )
    plot_rail_stations_map(
        train_stations_df,
        swiss_boundary_proj,
        output_path=str(FIGURES_DIR / "swiss_rail_stations.png"),
        show=False,
    )
    plot_station_meta_map(
        train_stations_dedup,
        swiss_boundary_proj,
        output_path=str(FIGURES_DIR / "swiss_rail_stations_deduplicated.png"),
        show=False,
    )


def build_reachability_comparison(
    swiss_train_meta: pd.DataFrame,
    trip_instances: dict,
    departures_by_station: dict,
    departure_times_by_station: dict,
) -> pd.DataFrame:
    origins = ["Lausanne", "Bern", "Genève", "Zürich HB"]
    departures = [6 * 60, 8 * 60, 12 * 60, 18 * 60]
    rows = []

    for origin in origins:
        start_key, _ = resolve_start_station(swiss_train_meta, swiss_train_meta, origin)
        engine = ReachabilityEngine(
            swiss_train_meta,
            trip_instances,
            departures_by_station,
            departure_times_by_station,
            start_key,
        )
        for dep in departures:
            rf = engine.build_reachable_frame(dep, 6 * 60)
            reachable_count = int(rf["reachable"].sum())
            rows.append(
                {
                    "origin": origin,
                    "departure_minutes": dep,
                    "departure_label": f"{dep // 60:02d}:00",
                    "reachable_count": reachable_count,
                    "reachable_share": reachable_count / len(swiss_train_meta),
                }
            )

    return pd.DataFrame(rows)


def export_per_station_reachability(
    swiss_train_meta: pd.DataFrame,
    trip_instances: dict,
    departures_by_station: dict,
    departure_times_by_station: dict,
    output_dir: Path,
) -> None:
    """
    For each (origin, departure_time) combination, export a JSON file with
    per-station reachability data suitable for frontend map rendering.

    Output file: reachability_{origin_slug}_{HHMM}.json
    Each record: {station_key, station_name, lat, lon, travel_minutes | null}
    """
    origins = ["Lausanne", "Bern", "Genève", "Zürich HB"]
    departures = [6 * 60, 8 * 60, 12 * 60, 18 * 60]

    # Also export a stations index once (lat/lon for all 1663 stations)
    stations_index = swiss_train_meta[["station_key", "station_name", "stop_lat", "stop_lon"]].copy()
    stations_index = stations_index.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})
    stations_index.to_json(output_dir / "stations.json", orient="records", indent=2)

    for origin in origins:
        origin_slug = origin.lower().replace(" ", "_").replace("ü", "u").replace("è", "e")
        start_key, start_row = resolve_start_station(swiss_train_meta, swiss_train_meta, origin)
        engine = ReachabilityEngine(
            swiss_train_meta,
            trip_instances,
            departures_by_station,
            departure_times_by_station,
            start_key,
        )
        for dep in departures:
            rf = engine.build_reachable_frame(dep, 6 * 60)
            out = rf[["station_key", "station_name", "stop_lat", "stop_lon", "travel_minutes"]].copy()
            out = out.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})
            # Replace NaN with None so JSON serialises as null
            out["travel_minutes"] = out["travel_minutes"].where(out["travel_minutes"].notna(), other=None)
            dep_label = f"{dep // 60:02d}{dep % 60:02d}"
            filename = f"reachability_{origin_slug}_{dep_label}.json"
            out.to_json(output_dir / filename, orient="records", indent=2)
            print(f"  Exported {filename} ({int(rf['reachable'].sum())} reachable stations)")


def main() -> None:
    apply_mpl_defaults()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading GTFS inputs...")
    stops_df = load_stops()
    routes_df = load_routes()
    trips_df = load_trips()
    calendar_df = load_calendar()
    calendar_dates_df = load_calendar_dates()
    stop_times_basic = load_stop_times_basic()

    swiss_boundary, swiss_boundary_proj = load_swiss_boundary()
    stops_inside = filter_stops_within_switzerland(stops_df, swiss_boundary)

    rail_routes_df = filter_rail_routes(routes_df)
    rail_trips_df = filter_rail_trips(trips_df, rail_routes_df)
    rail_stop_ids = filter_rail_stop_ids(stop_times_basic, rail_trips_df)
    train_stations_df = filter_rail_stations(stops_inside, rail_stop_ids)
    train_stations_dedup = build_station_meta(train_stations_df)

    export_static_maps(
        stops_inside=stops_inside,
        swiss_boundary_proj=swiss_boundary_proj,
        train_stations_df=train_stations_df,
        train_stations_dedup=train_stations_dedup,
    )

    active_services = compute_active_services(
        calendar_df,
        calendar_dates_df,
        ANALYSIS_DATE,
        max_elapsed_minutes=48 * 60,
    )
    active_rail = compute_active_rail_trips(rail_trips_df, active_services)
    active_trip_ids = set(active_rail["trip_id"].astype(str))
    swiss_train_stop_ids = set(train_stations_df["stop_id"].astype(str))

    stop_times_windowed = load_stop_times_hourly(
        data_dir=RAW_DATA_DIR,
        trip_ids=active_trip_ids,
        stop_ids=swiss_train_stop_ids,
    )
    stops_with_keys = train_stations_df[["stop_id", "station_key"]].drop_duplicates()
    station_windowed = (
        stop_times_windowed
        .merge(stops_with_keys, on="stop_id", how="left")
        .dropna(subset=["station_key"])
    )
    station_name_lookup = train_stations_dedup.set_index("station_key")["station_name"].to_dict()
    plot_busiest_stops(
        station_windowed,
        station_name_lookup,
        start_minutes=6 * 60,
        end_minutes=10 * 60,
        date_label=str(ANALYSIS_DATE.date()),
        output_path=str(FIGURES_DIR / "busiest_rail_stations_morning_peak.png"),
        show=False,
    )

    print("Building reachability graph...")
    stops_df = stops_df.copy()
    stops_df["stop_id"] = stops_df["stop_id"].astype(str)
    stops_df["station_key"] = stops_df["parent_station"].fillna("").astype(str).str.strip()
    stops_df["station_key"] = stops_df["station_key"].where(
        stops_df["station_key"].ne(""),
        stops_df["stop_id"],
    )
    active_st = load_active_stop_times(
        active_trip_ids,
        swiss_train_stop_ids,
        stops_df,
        active_rail,
    )
    trip_instances, departures_by_station, departure_times_by_station = build_trip_graph(active_st)
    swiss_train_meta = train_stations_dedup.copy()

    start_key, start_row = resolve_start_station(swiss_train_meta, swiss_train_meta, "Lausanne")
    engine = ReachabilityEngine(
        swiss_train_meta,
        trip_instances,
        departures_by_station,
        departure_times_by_station,
        start_key,
    )
    reachable_frame = engine.build_reachable_frame(8 * 60, 6 * 60)
    plot_reachability_map(
        reachable_frame,
        swiss_train_meta,
        start_row,
        swiss_boundary_proj,
        departure_minutes=8 * 60,
        elapsed_minutes=6 * 60,
        origin_label="Lausanne",
        output_path=str(FIGURES_DIR / "lausanne_reachability_0800_6h.png"),
        show=False,
    )

    comparison_df = build_reachability_comparison(
        swiss_train_meta,
        trip_instances,
        departures_by_station,
        departure_times_by_station,
    )
    comparison_df.to_csv(DATA_DIR / "reachability_comparison.csv", index=False)
    comparison_df.to_json(DATA_DIR / "reachability_comparison.json", orient="records", indent=2)
    plot_reachability_comparison_heatmap(
        comparison_df,
        output_path=str(FIGURES_DIR / "reachability_comparison_heatmap.png"),
        show=False,
    )

    summary = {
        "analysis_date": str(ANALYSIS_DATE.date()),
        "total_stops": int(len(stops_df)),
        "stops_inside_switzerland": int(len(stops_inside)),
        "rail_stop_entries": int(len(train_stations_df)),
        "rail_logical_stations": int(len(train_stations_dedup)),
        "active_rail_services": int(len(active_services)),
        "active_rail_trips": int(len(active_trip_ids)),
        "rail_stop_time_records": int(len(station_windowed)),
        "lausanne_reachable_6h_0800": int(reachable_frame["reachable"].sum()),
        "comparison_best_row": comparison_df.sort_values(
            ["reachable_share", "reachable_count"],
            ascending=False,
        ).iloc[0].to_dict(),
    }
    (DATA_DIR / "milestone1_summary.json").write_text(json.dumps(summary, indent=2))

    print("Exporting per-station reachability data for frontend...")
    export_per_station_reachability(
        swiss_train_meta,
        trip_instances,
        departures_by_station,
        departure_times_by_station,
        output_dir=DATA_DIR,
    )

    print(f"Exported figures to: {FIGURES_DIR}")
    print(f"Exported tables to:   {DATA_DIR}")


if __name__ == "__main__":
    main()
