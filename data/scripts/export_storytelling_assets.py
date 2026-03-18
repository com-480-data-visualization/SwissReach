"""
Export storytelling assets for the docs site.

This script builds three story layers:
1. 30-minute reachable supermarket / school / hospital counts from each rail station.
2. 60-minute IKEA access from each rail station.
3. Migros vs Coop store density views.

Outputs:
    docs/public/data/story_station_metrics_0800.json
    docs/public/data/story_pois_summary.json
    docs/public/data/migros_stores_min.json
    docs/public/data/coop_stores_min.json
    docs/public/figures/amenity_access_30min.png
    docs/public/figures/ikea_access_60min.png
    docs/public/figures/migros_vs_coop_density.png
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# Make sibling modules importable when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from config import ANALYSIS_DATE
from data_loader import (
    build_station_meta,
    filter_rail_routes,
    filter_rail_stop_ids,
    filter_rail_trips,
    load_calendar,
    load_calendar_dates,
    load_routes,
    load_stop_times_basic,
    load_stops,
    load_trips,
)
from reachability import (
    ReachabilityEngine,
    build_trip_graph,
    compute_active_rail_trips,
    compute_active_services,
    load_active_stop_times,
)
from spatial import load_swiss_boundary

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_data"
POI_CACHE_DIR = RAW_DATA_DIR / "story_pois"
SUPERMARKET_DIR = RAW_DATA_DIR / "supermarkets"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "public" / "data"
DOCS_FIG_DIR = PROJECT_ROOT / "docs" / "public" / "figures"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DEPARTURE_MINUTES = 8 * 60
HORIZON_MINUTES = 60

POI_SPECS: dict[str, dict[str, str]] = {
    "schools": {
        "title": "Schools",
        "query": """
[out:json][timeout:180];
area["ISO3166-1"="CH"][admin_level=2]->.ch;
(
  nwr["amenity"="school"](area.ch);
);
out center tags;
""".strip(),
    },
    "hospitals": {
        "title": "Hospitals",
        "query": """
[out:json][timeout:180];
area["ISO3166-1"="CH"][admin_level=2]->.ch;
(
  nwr["amenity"="hospital"](area.ch);
);
out center tags;
""".strip(),
    },
    "ikea": {
        "title": "IKEA",
        "query": """
[out:json][timeout:180];
area["ISO3166-1"="CH"][admin_level=2]->.ch;
(
  nwr["shop"="furniture"]["name"~"IKEA",i](area.ch);
  nwr["brand"~"IKEA",i](area.ch);
  nwr["name"~"IKEA",i]["shop"](area.ch);
);
out center tags;
""".strip(),
    },
}


def main() -> None:
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_FIG_DIR.mkdir(parents=True, exist_ok=True)
    POI_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading Swiss rail graph...")
    swiss_train_meta, boundary_wgs84, boundary_proj, trip_graph = build_reachability_context()

    print("Loading storytelling POIs...")
    poi_frames = {
        slug: load_or_fetch_poi_frame(slug, spec["query"])
        for slug, spec in POI_SPECS.items()
    }

    supermarkets = pd.read_csv(SUPERMARKET_DIR / "all_major_supermarkets.csv")
    supermarkets["category"] = "supermarkets"
    supermarkets["poi_name"] = supermarkets["name"].fillna(supermarkets["brand"])
    supermarkets["lon"] = pd.to_numeric(supermarkets["lon"], errors="coerce")
    supermarkets["lat"] = pd.to_numeric(supermarkets["lat"], errors="coerce")
    supermarkets = supermarkets.dropna(subset=["lat", "lon"]).copy()

    poi_frames["supermarkets"] = supermarkets[
        ["poi_name", "lon", "lat", "brand", "group", "layer", "retail_format", "source_url", "category"]
    ].copy()

    print("Assigning POIs to nearest rail stations...")
    station_reference = swiss_train_meta[["station_key", "station_name", "stop_lon", "stop_lat"]].copy()
    assigned_frames = {
        slug: assign_nearest_station(frame, station_reference)
        for slug, frame in poi_frames.items()
    }

    station_metrics = export_station_metrics(
        swiss_train_meta=swiss_train_meta,
        assigned_frames=assigned_frames,
        trip_graph=trip_graph,
    )

    print("Writing docs data...")
    write_docs_data(station_metrics, assigned_frames)

    print("Rendering figures...")
    render_amenity_access_figure(station_metrics, boundary_wgs84)
    render_ikea_access_figure(station_metrics, boundary_wgs84)
    render_migros_vs_coop_density_figure(assigned_frames["supermarkets"], boundary_proj)

    print(f"Done -> {DOCS_DATA_DIR} and {DOCS_FIG_DIR}")


def build_reachability_context():
    stops_df = load_stops()
    routes_df = load_routes()
    trips_df = load_trips()
    calendar_df = load_calendar()
    cal_dates_df = load_calendar_dates()
    stop_times_raw = load_stop_times_basic()
    boundary_wgs84, boundary_proj = load_swiss_boundary()

    rail_routes = filter_rail_routes(routes_df)
    rail_trips = filter_rail_trips(trips_df, rail_routes)
    rail_stop_ids = filter_rail_stop_ids(stop_times_raw, rail_trips)

    train_stops = stops_df[
        stops_df["stop_id"].astype(str).isin([str(s) for s in rail_stop_ids])
        & stops_df["stop_lat"].between(45.80, 47.85)
        & stops_df["stop_lon"].between(5.90, 10.55)
    ].copy()
    swiss_train_meta = build_station_meta(train_stops)

    active_services = compute_active_services(
        calendar_df, cal_dates_df, ANALYSIS_DATE, max_elapsed_minutes=48 * 60
    )
    active_rail = compute_active_rail_trips(rail_trips, active_services)
    active_trip_ids = set(active_rail["trip_id"].astype(str))
    swiss_stop_id_strs = set(train_stops["stop_id"].astype(str))

    stops_keyed = stops_df.copy()
    stops_keyed["stop_id"] = stops_keyed["stop_id"].astype(str)
    stops_keyed["station_key"] = stops_keyed["parent_station"].fillna("").astype(str).str.strip()
    stops_keyed["station_key"] = stops_keyed["station_key"].where(
        stops_keyed["station_key"].ne(""), stops_keyed["stop_id"]
    )

    active_st = load_active_stop_times(active_trip_ids, swiss_stop_id_strs, stops_keyed, active_rail)
    trip_instances, departures_by_station, departure_times_by_station = build_trip_graph(active_st)

    trip_graph = {
        "trip_instances": trip_instances,
        "departures_by_station": departures_by_station,
        "departure_times_by_station": departure_times_by_station,
    }
    return swiss_train_meta, boundary_wgs84, boundary_proj, trip_graph


def load_or_fetch_poi_frame(slug: str, query: str) -> pd.DataFrame:
    cache_path = POI_CACHE_DIR / f"{slug}.json"
    if cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        payload = fetch_overpass(query)
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for element in payload.get("elements", []):
        osm_type = element.get("type")
        osm_id = element.get("id")
        if osm_type not in {"node", "way", "relation"} or not isinstance(osm_id, int):
            continue
        key = (osm_type, osm_id)
        if key in seen:
            continue
        seen.add(key)

        lat = element.get("lat")
        lon = element.get("lon")
        if lat is None or lon is None:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
        if lat is None or lon is None:
            continue

        tags = element.get("tags", {})
        rows.append(
            {
                "poi_name": tags.get("name") or slug.title(),
                "lon": float(lon),
                "lat": float(lat),
                "source_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
                "category": slug,
            }
        )

    return pd.DataFrame(rows)


def fetch_overpass(query: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=180,
                headers={"User-Agent": "SwissReach storytelling exporter/1.0"},
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # requests raises multiple subclasses here
            last_error = exc
            if attempt == 3:
                break
            time.sleep(attempt * 2)
    raise RuntimeError(f"Overpass fetch failed: {last_error}") from last_error


def assign_nearest_station(poi_df: pd.DataFrame, station_df: pd.DataFrame) -> pd.DataFrame:
    poi_gdf = gpd.GeoDataFrame(
        poi_df.copy(),
        geometry=gpd.points_from_xy(poi_df["lon"], poi_df["lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")
    station_gdf = gpd.GeoDataFrame(
        station_df.copy(),
        geometry=gpd.points_from_xy(station_df["stop_lon"], station_df["stop_lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")

    station_coords = np.column_stack([station_gdf.geometry.x.to_numpy(), station_gdf.geometry.y.to_numpy()])
    poi_coords = np.column_stack([poi_gdf.geometry.x.to_numpy(), poi_gdf.geometry.y.to_numpy()])
    nearest_indices = np.empty(len(poi_gdf), dtype=int)
    nearest_distances = np.empty(len(poi_gdf), dtype=float)

    chunk_size = 1000
    for start in range(0, len(poi_gdf), chunk_size):
        end = min(start + chunk_size, len(poi_gdf))
        chunk = poi_coords[start:end]
        d2 = ((chunk[:, None, :] - station_coords[None, :, :]) ** 2).sum(axis=2)
        idx = d2.argmin(axis=1)
        nearest_indices[start:end] = idx
        nearest_distances[start:end] = np.sqrt(d2[np.arange(len(idx)), idx])

    matched = poi_gdf.copy()
    matched["station_key"] = station_gdf.iloc[nearest_indices]["station_key"].to_numpy()
    matched["station_name"] = station_gdf.iloc[nearest_indices]["station_name"].to_numpy()
    matched["station_distance_m"] = nearest_distances
    matched["x"] = matched.geometry.x
    matched["y"] = matched.geometry.y
    return pd.DataFrame(matched.drop(columns="geometry"))


def export_station_metrics(
    swiss_train_meta: pd.DataFrame,
    assigned_frames: dict[str, pd.DataFrame],
    trip_graph: dict[str, Any],
) -> pd.DataFrame:
    station_metrics = swiss_train_meta.copy()
    station_metrics["supermarkets_30min"] = 0
    station_metrics["schools_30min"] = 0
    station_metrics["hospitals_30min"] = 0
    station_metrics["ikea_60min"] = 0
    station_metrics["has_ikea_60min"] = False

    supermarket_counts = station_count_vector(swiss_train_meta, assigned_frames["supermarkets"])
    school_counts = station_count_vector(swiss_train_meta, assigned_frames["schools"])
    hospital_counts = station_count_vector(swiss_train_meta, assigned_frames["hospitals"])
    ikea_counts = station_count_vector(swiss_train_meta, assigned_frames["ikea"])

    keys = swiss_train_meta["station_key"].tolist()
    total = len(keys)
    for i, station_key in enumerate(keys, start=1):
        if i % 100 == 0 or i == total:
            print(f"  reachability metrics {i}/{total}")

        engine = ReachabilityEngine(
            swiss_train_meta,
            trip_graph["trip_instances"],
            trip_graph["departures_by_station"],
            trip_graph["departure_times_by_station"],
            station_key,
        )
        rf = engine.build_reachable_frame(DEPARTURE_MINUTES, HORIZON_MINUTES)
        travel = rf["travel_minutes"].to_numpy()
        reachable_30 = np.isfinite(travel) & (travel <= 30)
        reachable_60 = np.isfinite(travel) & (travel <= 60)

        idx = i - 1
        station_metrics.loc[idx, "supermarkets_30min"] = int(supermarket_counts[reachable_30].sum())
        station_metrics.loc[idx, "schools_30min"] = int(school_counts[reachable_30].sum())
        station_metrics.loc[idx, "hospitals_30min"] = int(hospital_counts[reachable_30].sum())
        station_metrics.loc[idx, "ikea_60min"] = int(ikea_counts[reachable_60].sum())
        station_metrics.loc[idx, "has_ikea_60min"] = bool(ikea_counts[reachable_60].sum() > 0)

    return station_metrics


def station_count_vector(swiss_train_meta: pd.DataFrame, poi_df: pd.DataFrame) -> np.ndarray:
    by_station = poi_df.groupby("station_key").size()
    return swiss_train_meta["station_key"].map(by_station).fillna(0).astype(int).to_numpy()


def write_docs_data(station_metrics: pd.DataFrame, assigned_frames: dict[str, pd.DataFrame]) -> None:
    station_metrics.to_json(
        DOCS_DATA_DIR / "story_station_metrics_0800.json",
        orient="records",
        indent=2,
    )

    summary = {
        "departure_time": "08:00",
        "station_count": int(len(station_metrics)),
        "poi_counts": {
            slug: int(len(df))
            for slug, df in assigned_frames.items()
        },
        "top_supermarket_station_30min": top_station_record(station_metrics, "supermarkets_30min"),
        "top_school_station_30min": top_station_record(station_metrics, "schools_30min"),
        "top_hospital_station_30min": top_station_record(station_metrics, "hospitals_30min"),
        "top_ikea_station_60min": top_station_record(station_metrics, "ikea_60min"),
    }
    (DOCS_DATA_DIR / "story_pois_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for slug in ["migros", "coop"]:
        stores = pd.read_csv(SUPERMARKET_DIR / f"{slug}_stores.csv")
        minimal = stores[["brand", "name", "lat", "lon", "city", "postcode", "source_url"]].copy()
        minimal.to_json(DOCS_DATA_DIR / f"{slug}_stores_min.json", orient="records", indent=2)


def top_station_record(df: pd.DataFrame, column: str) -> dict[str, Any]:
    row = df.sort_values(column, ascending=False).iloc[0]
    return {
        "station_key": row["station_key"],
        "station_name": row["station_name"],
        "value": int(row[column]),
    }


def render_amenity_access_figure(station_metrics: pd.DataFrame, boundary_wgs84: gpd.GeoDataFrame) -> None:
    gdf = gpd.GeoDataFrame(
        station_metrics.copy(),
        geometry=gpd.points_from_xy(station_metrics["stop_lon"], station_metrics["stop_lat"]),
        crs="EPSG:4326",
    )
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    specs = [
        ("supermarkets_30min", "30-min supermarkets", "Oranges"),
        ("schools_30min", "30-min schools", "Blues"),
        ("hospitals_30min", "30-min hospitals", "Reds"),
    ]
    for ax, (column, title, cmap) in zip(axes, specs):
        boundary_wgs84.plot(ax=ax, color="#f8fafc", edgecolor="#475569", linewidth=0.7)
        gdf.plot(
            ax=ax,
            column=column,
            cmap=cmap,
            markersize=10,
            alpha=0.85,
            legend=True,
            legend_kwds={"shrink": 0.7},
        )
        ax.set_title(title)
        ax.set_axis_off()
    fig.suptitle("Amenities reachable from each Swiss rail station within 30 minutes at 08:00", fontsize=14)
    fig.savefig(DOCS_FIG_DIR / "amenity_access_30min.png", bbox_inches="tight")
    plt.close(fig)


def render_ikea_access_figure(station_metrics: pd.DataFrame, boundary_wgs84: gpd.GeoDataFrame) -> None:
    gdf = gpd.GeoDataFrame(
        station_metrics.copy(),
        geometry=gpd.points_from_xy(station_metrics["stop_lon"], station_metrics["stop_lat"]),
        crs="EPSG:4326",
    )
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    boundary_wgs84.plot(ax=ax, color="#f8fafc", edgecolor="#475569", linewidth=0.8)
    gdf[gdf["has_ikea_60min"]].plot(ax=ax, color="#0f766e", markersize=12, alpha=0.9, label="Can reach IKEA in 60 min")
    gdf[~gdf["has_ikea_60min"]].plot(ax=ax, color="#cbd5e1", markersize=8, alpha=0.4, label="No IKEA in 60 min")
    ax.set_title("Swiss rail stations with IKEA access within 60 minutes at 08:00")
    ax.set_axis_off()
    ax.legend(loc="lower left", frameon=True)
    fig.savefig(DOCS_FIG_DIR / "ikea_access_60min.png", bbox_inches="tight")
    plt.close(fig)


def render_migros_vs_coop_density_figure(supermarkets: pd.DataFrame, boundary_proj: gpd.GeoDataFrame) -> None:
    subset = supermarkets[supermarkets["brand"].isin(["Migros", "Coop"])].copy()
    gdf = gpd.GeoDataFrame(
        subset,
        geometry=gpd.points_from_xy(subset["lon"], subset["lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")

    migros = gdf[gdf["brand"] == "Migros"]
    coop = gdf[gdf["brand"] == "Coop"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    xlim = boundary_proj.total_bounds[[0, 2]]
    ylim = boundary_proj.total_bounds[[1, 3]]

    for ax, title in zip(
        axes,
        ["Migros density", "Coop density", "Coop minus Migros density"],
    ):
        boundary_proj.plot(ax=ax, color="#f8fafc", edgecolor="#475569", linewidth=0.7)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_axis_off()
        ax.set_title(title)

    hb1 = axes[0].hexbin(migros.geometry.x, migros.geometry.y, gridsize=32, cmap="Oranges", mincnt=1, alpha=0.85)
    hb2 = axes[1].hexbin(coop.geometry.x, coop.geometry.y, gridsize=32, cmap="Blues", mincnt=1, alpha=0.85)

    diff_extent = [xlim[0], xlim[1], ylim[0], ylim[1]]
    migros_hist, xedges, yedges = np.histogram2d(migros.geometry.x, migros.geometry.y, bins=28, range=[[xlim[0], xlim[1]], [ylim[0], ylim[1]]])
    coop_hist, _, _ = np.histogram2d(coop.geometry.x, coop.geometry.y, bins=[xedges, yedges])
    diff = (coop_hist - migros_hist).T
    vmax = np.abs(diff).max() or 1
    mesh = axes[2].pcolormesh(xedges, yedges, diff, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="auto", alpha=0.75)

    fig.colorbar(hb1, ax=axes[0], shrink=0.75)
    fig.colorbar(hb2, ax=axes[1], shrink=0.75)
    fig.colorbar(mesh, ax=axes[2], shrink=0.75)
    fig.suptitle("Migros vs Coop store density in Switzerland", fontsize=14)
    fig.savefig(DOCS_FIG_DIR / "migros_vs_coop_density.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
