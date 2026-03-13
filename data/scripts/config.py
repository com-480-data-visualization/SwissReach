"""
Global configuration for Swiss public transport reachability analysis.

All tuneable constants, file paths, and GTFS parameters live here
so the notebook and other modules stay free of magic numbers.
"""

import os
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "..", "raw_data")

# ── GTFS route types recognised as "rail" ────────────────────────────
# 2        = conventional rail (GTFS standard)
# 100–109  = Swiss-specific subtypes (S-Bahn, IC, IR, RE, …)
RAIL_ROUTE_TYPES = [2, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]

# ── Analysis parameters ──────────────────────────────────────────────
ANALYSIS_DATE = pd.Timestamp("2026-03-18")
MIN_TRANSFER_MINUTES = 3
MAX_ELAPSED_MINUTES = 48 * 60
DEFAULT_DEPARTURE_MINUTES = 8 * 60   # 08:00
DEFAULT_HORIZON_MINUTES = 6 * 60

# Backward-compatible hour aliases for older notebook cells/scripts.
MAX_ELAPSED_HOURS = MAX_ELAPSED_MINUTES // 60
DEFAULT_HORIZON_HOURS = DEFAULT_HORIZON_MINUTES // 60

# ── Default origin station ───────────────────────────────────────────
START_STATION_NAME = "Lausanne"

# ── Swiss boundary (local file, downloaded by download_sbb_gtfs.py) ──
SWISS_BOUNDARY_GEOJSON = os.path.join(RAW_DATA_DIR, "swiss_boundary.geojson")

# ── Matplotlib defaults ─────────────────────────────────────────────
MPL_FONT_FAMILIES = ["PingFang SC", "Arial Unicode MS", "DejaVu Sans"]

# ── Chunked reading ─────────────────────────────────────────────────
STOP_TIMES_CHUNK_SIZE = 2_000_000
