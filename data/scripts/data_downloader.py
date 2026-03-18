import json
import os
import zipfile

import requests

# Define absolute paths based on this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR represents the 'data' folder
DATA_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_EXTRACT_DIR = os.path.join(DATA_DIR, "raw_data")

# ── URLs (only used inside this download script) ─────────────────────
_GTFS_PERMALINK = "https://data.opentransportdata.swiss/dataset/timetable-2026-gtfs2020/permalink"
_SWISS_BOUNDARY_API_URL = (
    "https://api3.geo.admin.ch/rest/services/api/MapServer/"
    "ch.swisstopo.swissboundaries3d-land-flaeche.fill/CH"
    "?geometryFormat=geojson&sr=2056"
)
_CANTON_BOUNDARY_API_BASE = (
    "https://api3.geo.admin.ch/rest/services/api/MapServer/"
    "ch.swisstopo.swissboundaries3d-kanton-flaeche.fill"
)
_VAUD_CANTON_ID = 22


def download_sbb_gtfs(extract_dir=DEFAULT_EXTRACT_DIR):
    """Download and extract the SBB GTFS static timetable."""
    print("Connecting to official SBB permalink to fetch the latest GTFS data...")

    try:
        zip_filename = os.path.join(DATA_DIR, "sbb_gtfs_temp.zip")
        print("Starting dataset download...")

        with requests.get(_GTFS_PERMALINK, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with open(zip_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"Download completed. Extracting to directory: {extract_dir}/")

        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        os.remove(zip_filename)
        print("Done. The dataset is ready for use.")

        extracted_files = os.listdir(extract_dir)
        print(f"Total files extracted: {len(extracted_files)}. Examples: {', '.join(extracted_files[:5])}...")

    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
    except zipfile.BadZipFile:
        print("Error: The downloaded ZIP file is corrupted.")
    except Exception as e:
        print(f"An unknown error occurred: {e}")


def download_swiss_boundary(extract_dir=DEFAULT_EXTRACT_DIR):
    """Download the SwissBoundaries3D national outline as a local GeoJSON file."""
    dest = os.path.join(extract_dir, "swiss_boundary.geojson")
    print("Downloading Swiss national boundary from swisstopo API...")

    try:
        response = requests.get(_SWISS_BOUNDARY_API_URL)
        response.raise_for_status()
        json_data = response.json()

        os.makedirs(extract_dir, exist_ok=True)
        with open(dest, "w") as f:
            json.dump(json_data, f)

        print(f"Saved to {dest}")
    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")


def download_vaud_boundary(extract_dir=DEFAULT_EXTRACT_DIR):
    """Download Vaud canton boundary (VD, BFS id 22) as local GeoJSON."""
    dest = os.path.join(extract_dir, "vaud_boundary.geojson")
    url = (
        f"{_CANTON_BOUNDARY_API_BASE}/{_VAUD_CANTON_ID}"
        "?geometryFormat=geojson&sr=2056"
    )
    print("Downloading Vaud canton boundary from swisstopo API...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()

        os.makedirs(extract_dir, exist_ok=True)
        with open(dest, "w") as f:
            json.dump(json_data, f)

        print(f"Saved to {dest}")
    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")


if __name__ == "__main__":
    download_sbb_gtfs()
    download_swiss_boundary()
    download_vaud_boundary()