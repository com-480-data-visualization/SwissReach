"""
Visualisation functions for Swiss public transport analysis.

Each public function produces one self-contained figure.
"""

from __future__ import annotations

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import MIN_TRANSFER_MINUTES, MPL_FONT_FAMILIES


def apply_mpl_defaults():
    """Set matplotlib font stack for CJK + Latin extended characters."""
    plt.rcParams["font.sans-serif"] = MPL_FONT_FAMILIES
    plt.rcParams["axes.unicode_minus"] = False


# ── Helpers ──────────────────────────────────────────────────────────

def _minutes_to_clock(total_minutes: float) -> str:
    hours = int(total_minutes // 60) % 24
    minutes = int(total_minutes % 60)
    return f"{hours:02d}:{minutes:02d}"


def _minutes_to_duration(total_minutes: float) -> str:
    total_minutes = int(round(total_minutes))
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours} h {minutes:02d} min"
    if hours:
        return f"{hours} h"
    return f"{minutes} min"


# ── 1. All-stops map ────────────────────────────────────────────────

def plot_stops_map(
    stops_gdf: gpd.GeoDataFrame,
    boundary_proj: gpd.GeoDataFrame,
) -> None:
    """
    Plot all Swiss public-transport stops on the EPSG:2056 map.
    """
    stops_proj = stops_gdf.to_crs("EPSG:2056")

    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    boundary_proj.plot(ax=ax, color="#eef2f7", edgecolor="#4a6fa5", linewidth=1.5)
    stops_proj.plot(ax=ax, markersize=0.6, color="#e05c97", alpha=0.45)
    ax.set_aspect("equal")
    ax.set_title(
        "Swiss Public Transport Stops\n(filtered by SwissBoundaries3D)",
        fontsize=13, fontweight="bold", pad=12,
    )
    ax.axis("off")
    fig.tight_layout(pad=2)
    plt.show()


# ── 2. Rail stations map ────────────────────────────────────────────

def plot_rail_stations_map(
    train_stations_gdf: gpd.GeoDataFrame,
    boundary_proj: gpd.GeoDataFrame,
) -> None:
    """
    Plot Swiss rail stations on the EPSG:2056 map.
    """
    train_proj = train_stations_gdf.to_crs("EPSG:2056")

    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    boundary_proj.plot(ax=ax, color="#f0f4f8", edgecolor="#4a6fa5", linewidth=1.5)
    train_proj.plot(
        ax=ax, markersize=5, color="#e05c97", alpha=0.8,
        label=f"Rail stations ({len(train_stations_gdf):,})",
    )
    ax.set_aspect("equal")
    ax.set_title("Swiss Rail Stations", fontsize=14, fontweight="bold", pad=12)
    ax.legend(loc="lower left", fontsize=10, framealpha=0.85)
    ax.axis("off")
    fig.tight_layout(pad=2)
    plt.show()


# ── 2b. Deduplicated rail stations map ──────────────────────────────

def plot_station_meta_map(
    station_meta: pd.DataFrame,
    boundary_proj: gpd.GeoDataFrame,
) -> None:
    """
    Plot deduplicated rail stations (output of build_station_meta) on the EPSG:2056 map.
    Expects columns: stop_lat, stop_lon, station_name.
    """
    gdf = gpd.GeoDataFrame(
        station_meta,
        geometry=gpd.points_from_xy(station_meta["stop_lon"], station_meta["stop_lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")

    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    boundary_proj.plot(ax=ax, color="#f0f4f8", edgecolor="#4a6fa5", linewidth=1.5)
    gdf.plot(
        ax=ax, markersize=5, color="#e05c97", alpha=0.8,
        label=f"Rail stations (deduplicated, {len(station_meta):,})",
    )
    ax.set_aspect("equal")
    ax.set_title(
        "Swiss Rail Stations (Deduplicated)",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.legend(loc="lower left", fontsize=10, framealpha=0.85)
    ax.axis("off")
    fig.tight_layout(pad=2)
    plt.show()


# ── 3. Busiest stops bar chart ───────────────────────────────────────

def plot_busiest_stops(
    stop_times_windowed: pd.DataFrame,
    station_name_lookup: dict,
    start_minutes: int = 6 * 60,
    end_minutes: int = 10 * 60,
    date_label: str | None = None,
) -> None:
    """
    Horizontal bar chart of the 10 busiest rail stations in a minute-precision window.
    """
    if start_minutes >= end_minutes:
        print("Start time must be earlier than end time.")
        return

    mask = (
        (stop_times_windowed["departure_minutes"] >= start_minutes)
        & (stop_times_windowed["departure_minutes"] < end_minutes)
    )
    busiest = (
        stop_times_windowed.loc[mask]
        .groupby("station_key")["trip_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )

    if busiest.empty:
        print(
            "No active rail trips in "
            f"{_minutes_to_clock(start_minutes)} – {_minutes_to_clock(end_minutes)}."
        )
        return

    labels = [station_name_lookup.get(station_key, station_key) for station_key in busiest.index]
    # Color intensity proportional to value (normalised to 0–1)
    vmin, vmax = busiest.values.min(), busiest.values.max()
    normed = (busiest.values - vmin) / max(vmax - vmin, 1)
    cmap = plt.cm.get_cmap("YlOrRd")
    colors = [cmap(0.25 + 0.7 * v) for v in normed]  # avoid near-white

    fig, ax = plt.subplots(figsize=(11, 5), facecolor="white")
    ax.barh(labels, busiest.values, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Unique rail trips", fontsize=12)
    title_suffix = f" on {date_label}" if date_label else ""
    ax.set_title(
        "Top 10 Busiest Rail Stations"
        f"{title_suffix}  ({_minutes_to_clock(start_minutes)} – {_minutes_to_clock(end_minutes)})",
        fontsize=13, fontweight="bold",
    )
    ax.tick_params(axis="y", labelsize=9)
    ax.xaxis.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    plt.show()


# ── 4. Reachability map ─────────────────────────────────────────────

def plot_reachability_map(
    reachable_frame: pd.DataFrame,
    swiss_train_meta: pd.DataFrame,
    start_station_row: pd.Series,
    boundary_proj: gpd.GeoDataFrame,
    departure_minutes: int,
    elapsed_minutes: int,
    origin_label: str = "Lausanne",
) -> None:
    """
    Choropleth-style scatter map showing rail reachability from an origin.
    """
    gdf_stations = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(swiss_train_meta["stop_lon"], swiss_train_meta["stop_lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")
    gdf_stations["station_key"] = swiss_train_meta["station_key"].values

    start_gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy([start_station_row["stop_lon"]], [start_station_row["stop_lat"]]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2056")
    start_x = start_gdf.geometry.x.values[0]
    start_y = start_gdf.geometry.y.values[0]

    # Map extent
    minx, miny, maxx, maxy = boundary_proj.total_bounds
    width, height = maxx - minx, maxy - miny
    x_pad, y_pad = width * 0.04, height * 0.04
    fig_w = 16
    fig_h = fig_w * (height / width) if width else fig_w

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150, facecolor="white")
    boundary_proj.plot(ax=ax, color="#f0f4f8", edgecolor="#4a6fa5", linewidth=1.2)

    gdf_all = gdf_stations.merge(
        reachable_frame[["station_key", "reachable", "travel_minutes"]],
        on="station_key", how="left",
    )

    unreachable = gdf_all[~gdf_all["reachable"].fillna(False)]
    reachable_gdf = gdf_all[gdf_all["reachable"].fillna(False)]

    ax.scatter(
        unreachable.geometry.x, unreachable.geometry.y,
        s=6, color="#cfd8dc", alpha=0.5, label="Not reachable", zorder=2,
    )

    if not reachable_gdf.empty:
        scatter = ax.scatter(
            reachable_gdf.geometry.x, reachable_gdf.geometry.y,
            c=reachable_gdf["travel_minutes"], s=32, cmap="plasma_r",
            vmin=0, vmax=elapsed_minutes, alpha=0.92,
            label="Reachable stations", zorder=3,
        )
        cbar = fig.colorbar(scatter, ax=ax, shrink=0.78, pad=0.02)
        cbar.set_label("Travel time (minutes)", fontsize=11)
        cbar.ax.tick_params(labelsize=9)

    ax.scatter(
        [start_x], [start_y],
        color="#d62728", s=300, marker="*", label=origin_label, zorder=5,
    )

    ax.set_xlim(minx - x_pad, maxx + x_pad)
    ax.set_ylim(miny - y_pad, maxy + y_pad)
    ax.set_title(
        f"Swiss Railway Reachability from {origin_label}\n"
        f"Departure {_minutes_to_clock(departure_minutes)}  |  "
        f"Window {_minutes_to_duration(elapsed_minutes)}  |  "
        f"Min transfer {MIN_TRANSFER_MINUTES} min",
        fontsize=15, fontweight="bold",
    )
    ax.set_xlabel("Easting (m)", fontsize=11)
    ax.set_ylabel("Northing (m)", fontsize=11)
    ax.tick_params(axis="both", labelsize=9)
    ax.legend(loc="lower left", fontsize=10, framealpha=0.9)
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()

    reachable_count = int(reachable_gdf["reachable"].sum())
    total = len(swiss_train_meta)
    print(
        f"Departure: {_minutes_to_clock(departure_minutes)} | "
        f"Window: {_minutes_to_duration(elapsed_minutes)} | "
        f"Reachable: {reachable_count}/{total}"
    )
    plt.show()
