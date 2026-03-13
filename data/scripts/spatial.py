"""
Spatial utilities: Swiss boundary loading and point-in-polygon filtering.
"""

from __future__ import annotations

import json

import geopandas as gpd
import pandas as pd

from config import SWISS_BOUNDARY_GEOJSON
from data_loader import derive_station_key


# ── Swiss boundary ───────────────────────────────────────────────────

def load_swiss_boundary() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load the SwissBoundaries3D national outline from a local GeoJSON file
    (downloaded by ``download_sbb_gtfs.py``).

    Returns
    -------
    boundary_wgs84 : GeoDataFrame in EPSG:4326
    boundary_proj  : GeoDataFrame in EPSG:2056
    """
    with open(SWISS_BOUNDARY_GEOJSON, "r") as f:
        json_data = json.load(f)

    boundary_proj = gpd.GeoDataFrame.from_features(
        [json_data["feature"]], crs="EPSG:2056"
    )
    boundary_wgs84 = boundary_proj.to_crs("EPSG:4326")
    return boundary_wgs84, boundary_proj


# ── Stop filtering ───────────────────────────────────────────────────

def filter_stops_within_switzerland(
    stops_df: pd.DataFrame,
    boundary_wgs84: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Keep only stops whose coordinates fall inside the Swiss national boundary.
    """
    gdf = gpd.GeoDataFrame(
        stops_df,
        geometry=gpd.points_from_xy(stops_df.stop_lon, stops_df.stop_lat),
        crs="EPSG:4326",
    )
    return gdf[gdf.geometry.within(boundary_wgs84.unary_union)].copy()


def filter_rail_stations(
    stops_inside: gpd.GeoDataFrame,
    rail_stop_ids,
) -> gpd.GeoDataFrame:
    """
    From the Swiss-filtered stops, keep only those served by rail trips.
    """
    df = stops_inside[stops_inside["stop_id"].isin(rail_stop_ids)].copy()
    df["stop_id"] = df["stop_id"].astype(str)
    df["station_key"] = derive_station_key(df)
    return df
