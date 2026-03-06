import requests
import zipfile
import os

# Define absolute paths based on this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR represents the 'data' folder
DATA_DIR = os.path.dirname(SCRIPT_DIR)
DEFAULT_EXTRACT_DIR = os.path.join(DATA_DIR, "raw_data")

def download_sbb_gtfs(extract_dir=DEFAULT_EXTRACT_DIR):
    # Official SBB 2026 GTFS static data permalink
    # No API Key required, directly downloads the latest version
    permalink_url = "https://data.opentransportdata.swiss/dataset/timetable-2026-gtfs2020/permalink"

    print("Connecting to official SBB permalink to fetch the latest GTFS data...")

    try:
        # Save temp zip in the data directory
        zip_filename = os.path.join(DATA_DIR, "sbb_gtfs_temp.zip")
        print("Starting dataset download...")

        # Use allow_redirects=True to follow redirects to the actual zip file URL
        with requests.get(permalink_url, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with open(zip_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"Download completed. Extracting to directory: ./{extract_dir}/")

        # Extract the contents of the zip file
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Clean up the temporary zip file
        os.remove(zip_filename)
        print("Done. The dataset is ready for use.")

        # List core files to verify extraction
        extracted_files = os.listdir(extract_dir)
        print(f"Total files extracted: {len(extracted_files)}. Examples: {', '.join(extracted_files[:5])}...")

    except requests.exceptions.RequestException as e:
        print(f"Network request failed: {e}")
    except zipfile.BadZipFile:
        print("Error: The downloaded ZIP file is corrupted.")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

if __name__ == "__main__":
    download_sbb_gtfs()
