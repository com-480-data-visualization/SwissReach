"""
Download Swiss food retail location datasets from OpenStreetMap.

The script uses Overpass once for Switzerland-wide food retail POIs, then
splits the result into brand-specific and layer-specific CSV/JSON exports.

Usage:
    .venv/bin/python data/scripts/fetch_swiss_supermarkets.py
    .venv/bin/python data/scripts/fetch_swiss_supermarkets.py --brands migros coop denner
    .venv/bin/python data/scripts/fetch_swiss_supermarkets.py --output-dir data/raw_data/custom_supermarkets
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw_data" / "supermarkets"
DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DEFAULT_TIMEOUT_SECONDS = 180
OVERPASS_QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="CH"][admin_level=2]->.ch;
(
  nwr["shop"~"^(supermarket|convenience|department_store)$"](area.ch);
);
out center tags;
"""


@dataclass(frozen=True)
class BrandTarget:
    slug: str
    label: str
    group: str
    layer: str
    retail_format: str
    allowed_shops: tuple[str, ...]
    tag_aliases: tuple[str, ...]
    name_aliases: tuple[str, ...] = ()
    exclude_aliases: tuple[str, ...] = ()


BRANDS: tuple[BrandTarget, ...] = (
    BrandTarget(
        slug="migros",
        label="Migros",
        group="Migros",
        layer="supermarket_core",
        retail_format="supermarket",
        allowed_shops=("supermarket", "convenience"),
        tag_aliases=("migros", "migros supermarkt", "migros partner", "voi migros partner"),
        name_aliases=("migros", "voi migros partner"),
        exclude_aliases=("migrolino", "mio by migrolino", "gooods"),
    ),
    BrandTarget(
        slug="coop",
        label="Coop",
        group="Coop",
        layer="supermarket_core",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("coop",),
        name_aliases=("coop",),
        exclude_aliases=("coop pronto",),
    ),
    BrandTarget(
        slug="denner",
        label="Denner",
        group="Migros",
        layer="supermarket_core",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("denner",),
        name_aliases=("denner",),
    ),
    BrandTarget(
        slug="lidl",
        label="Lidl",
        group="Lidl",
        layer="supermarket_core",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("lidl", "lidl schweiz"),
        name_aliases=("lidl",),
    ),
    BrandTarget(
        slug="aldi",
        label="ALDI SUISSE",
        group="ALDI SUISSE",
        layer="supermarket_core",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("aldi suisse", "aldi suisse ag", "aldi suisse sa", "aldi"),
        name_aliases=("aldi", "aldi suisse"),
    ),
    BrandTarget(
        slug="manor_food",
        label="Manor Food",
        group="Manor",
        layer="supermarket_secondary",
        retail_format="supermarket",
        allowed_shops=("supermarket", "department_store"),
        tag_aliases=("manor food",),
        name_aliases=("manor food",),
    ),
    BrandTarget(
        slug="volg",
        label="Volg",
        group="Volg",
        layer="supermarket_secondary",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("volg",),
        name_aliases=("volg",),
    ),
    BrandTarget(
        slug="spar",
        label="SPAR",
        group="SPAR",
        layer="supermarket_secondary",
        retail_format="supermarket",
        allowed_shops=("supermarket",),
        tag_aliases=("spar", "spar schweiz"),
        name_aliases=("spar",),
        exclude_aliases=("spar express",),
    ),
    BrandTarget(
        slug="migrolino",
        label="migrolino",
        group="Migros",
        layer="convenience",
        retail_format="convenience",
        allowed_shops=("supermarket", "convenience"),
        tag_aliases=("migrolino",),
        name_aliases=("migrolino", "mio by migrolino", "gooods"),
    ),
    BrandTarget(
        slug="coop_pronto",
        label="Coop Pronto",
        group="Coop",
        layer="convenience",
        retail_format="convenience",
        allowed_shops=("supermarket", "convenience"),
        tag_aliases=("coop pronto",),
        name_aliases=("coop pronto",),
    ),
    BrandTarget(
        slug="avec",
        label="avec",
        group="Valora",
        layer="convenience",
        retail_format="convenience",
        allowed_shops=("convenience",),
        tag_aliases=("avec", "avec."),
        name_aliases=("avec", "avec express"),
    ),
)

BRAND_BY_SLUG = {brand.slug: brand for brand in BRANDS}
CSV_COLUMNS = [
    "brand",
    "brand_slug",
    "group",
    "layer",
    "retail_format",
    "name",
    "shop",
    "street",
    "house_number",
    "postcode",
    "city",
    "canton",
    "country",
    "address",
    "osm_brand",
    "osm_operator",
    "lat",
    "lon",
    "osm_type",
    "osm_id",
    "website",
    "phone",
    "opening_hours",
    "source_url",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Swiss food retail locations for selected Swiss brands."
    )
    parser.add_argument(
        "--brands",
        nargs="+",
        choices=sorted(BRAND_BY_SLUG),
        default=sorted(BRAND_BY_SLUG),
        help="Brand slugs to export. Defaults to all configured brands.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for CSV/JSON exports. Defaults to {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--overpass-url",
        default=DEFAULT_OVERPASS_URL,
        help=f"Overpass endpoint. Defaults to {DEFAULT_OVERPASS_URL}.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout in seconds. Defaults to {DEFAULT_TIMEOUT_SECONDS}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = [BRAND_BY_SLUG[slug] for slug in args.brands]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Requesting Switzerland-wide food retail POIs from Overpass...")
    response = fetch_overpass(
        overpass_url=args.overpass_url,
        timeout_seconds=args.timeout,
        max_attempts=3,
    )
    elements = response.get("elements", [])
    print(f"Received {len(elements)} OSM elements")

    matched_rows_by_brand: dict[str, list[dict[str, Any]]] = {brand.slug: [] for brand in targets}
    seen_keys_by_brand: dict[str, set[tuple[str, int]]] = {brand.slug: set() for brand in targets}

    for element in elements:
        row = element_to_row(element)
        if row is None:
            continue

        for brand in targets:
            if not matches_brand(row=row, brand=brand):
                continue

            key = (row["osm_type"], row["osm_id"])
            if key in seen_keys_by_brand[brand.slug]:
                continue

            brand_row = dict(row)
            brand_row["brand"] = brand.label
            brand_row["brand_slug"] = brand.slug
            brand_row["group"] = brand.group
            brand_row["layer"] = brand.layer
            brand_row["retail_format"] = brand.retail_format
            matched_rows_by_brand[brand.slug].append(brand_row)
            seen_keys_by_brand[brand.slug].add(key)

    combined_rows: list[dict[str, Any]] = []
    layer_rows: dict[str, list[dict[str, Any]]] = {}
    for brand in targets:
        rows = sorted(
            matched_rows_by_brand[brand.slug],
            key=lambda item: (
                safe_sort_value(item["city"]),
                safe_sort_value(item["postcode"]),
                safe_sort_value(item["name"]),
                item["osm_id"],
            ),
        )
        combined_rows.extend(rows)
        layer_rows.setdefault(brand.layer, []).extend(rows)
        write_brand_exports(output_dir=args.output_dir, brand=brand, rows=rows)
        print(f"Exported {len(rows):4d} rows for {brand.slug}")

    combined_rows.sort(
        key=lambda item: (
            item["layer"],
            item["brand_slug"],
            safe_sort_value(item["city"]),
            safe_sort_value(item["postcode"]),
            safe_sort_value(item["name"]),
            item["osm_id"],
        )
    )
    write_combined_exports(output_dir=args.output_dir, rows=combined_rows)
    write_layer_exports(output_dir=args.output_dir, layer_rows=layer_rows)
    print(f"Done -> {args.output_dir}")
    return 0


def fetch_overpass(
    overpass_url: str,
    timeout_seconds: int,
    max_attempts: int,
) -> dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(
                overpass_url,
                data={"data": OVERPASS_QUERY},
                timeout=timeout_seconds,
                headers={"User-Agent": "SwissReach supermarket exporter/1.0"},
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Overpass response was not a JSON object")
            return payload
        except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            sleep_seconds = attempt * 2
            print(
                f"Overpass attempt {attempt}/{max_attempts} failed: {exc}. "
                f"Retrying in {sleep_seconds}s...",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)

    raise RuntimeError(f"Failed to fetch data from Overpass: {last_error}") from last_error


def element_to_row(element: dict[str, Any]) -> dict[str, Any] | None:
    tags = element.get("tags")
    if not isinstance(tags, dict):
        return None

    lat, lon = element_coordinates(element)
    if lat is None or lon is None:
        return None

    osm_type = element.get("type")
    osm_id = element.get("id")
    if osm_type not in {"node", "way", "relation"} or not isinstance(osm_id, int):
        return None

    street = clean_tag(tags.get("addr:street"))
    house_number = clean_tag(tags.get("addr:housenumber"))
    postcode = clean_tag(tags.get("addr:postcode"))
    city = clean_tag(tags.get("addr:city")) or clean_tag(tags.get("addr:place"))
    canton = clean_tag(tags.get("addr:state")) or clean_tag(tags.get("addr:province"))
    country = clean_tag(tags.get("addr:country")) or "CH"
    name = (
        clean_tag(tags.get("name"))
        or clean_tag(tags.get("brand"))
        or clean_tag(tags.get("operator"))
    )

    row = {
        "brand": "",
        "brand_slug": "",
        "group": "",
        "layer": "",
        "retail_format": "",
        "name": name,
        "shop": clean_tag(tags.get("shop")),
        "street": street,
        "house_number": house_number,
        "postcode": postcode,
        "city": city,
        "canton": canton,
        "country": country,
        "address": format_address(street, house_number, postcode, city, country, tags),
        "osm_brand": clean_tag(tags.get("brand")),
        "osm_operator": clean_tag(tags.get("operator")),
        "lat": lat,
        "lon": lon,
        "osm_type": osm_type,
        "osm_id": osm_id,
        "website": clean_tag(tags.get("website")) or clean_tag(tags.get("contact:website")),
        "phone": clean_tag(tags.get("phone")) or clean_tag(tags.get("contact:phone")),
        "opening_hours": clean_tag(tags.get("opening_hours")),
        "source_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
        "_name": lowercase(clean_tag(tags.get("name"))),
        "_brand": lowercase(clean_tag(tags.get("brand"))),
        "_operator": lowercase(clean_tag(tags.get("operator"))),
    }
    return row


def element_coordinates(element: dict[str, Any]) -> tuple[float | None, float | None]:
    lat = element.get("lat")
    lon = element.get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon)

    center = element.get("center")
    if isinstance(center, dict):
        center_lat = center.get("lat")
        center_lon = center.get("lon")
        if isinstance(center_lat, (int, float)) and isinstance(center_lon, (int, float)):
            return float(center_lat), float(center_lon)

    return None, None


def matches_brand(row: dict[str, Any], brand: BrandTarget) -> bool:
    if row["shop"] not in brand.allowed_shops:
        return False

    values_to_match = (
        row["_brand"],
        row["_operator"],
        row["_name"],
    )
    if any(
        value.startswith(alias)
        for value in values_to_match
        for alias in brand.exclude_aliases
        if value and alias
    ):
        return False

    if any(value in brand.tag_aliases for value in values_to_match if value):
        return True

    if any(
        value.startswith(alias)
        for value in values_to_match
        for alias in brand.name_aliases
        if value and alias
    ):
        return True

    return False


def write_brand_exports(output_dir: Path, brand: BrandTarget, rows: list[dict[str, Any]]) -> None:
    csv_path = output_dir / f"{brand.slug}_stores.csv"
    json_path = output_dir / f"{brand.slug}_stores.json"
    write_csv(csv_path, rows)
    write_json(json_path, rows)


def write_combined_exports(output_dir: Path, rows: list[dict[str, Any]]) -> None:
    write_csv(output_dir / "all_food_retail.csv", rows)
    write_json(output_dir / "all_food_retail.json", rows)
    supermarket_rows = [row for row in rows if row.get("layer") != "convenience"]
    write_csv(output_dir / "all_major_supermarkets.csv", supermarket_rows)
    write_json(output_dir / "all_major_supermarkets.json", supermarket_rows)


def write_layer_exports(output_dir: Path, layer_rows: dict[str, list[dict[str, Any]]]) -> None:
    for layer, rows in sorted(layer_rows.items()):
        rows = sorted(
            rows,
            key=lambda item: (
                item["brand_slug"],
                safe_sort_value(item["city"]),
                safe_sort_value(item["postcode"]),
                safe_sort_value(item["name"]),
                item["osm_id"],
            ),
        )
        write_csv(output_dir / f"{layer}.csv", rows)
        write_json(output_dir / f"{layer}.json", rows)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(public_row(row))


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    serializable_rows = [public_row(row) for row in rows]
    path.write_text(json.dumps(serializable_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def public_row(row: dict[str, Any]) -> dict[str, Any]:
    return {column: row.get(column) for column in CSV_COLUMNS}


def clean_tag(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def lowercase(value: str) -> str:
    return value.casefold().strip() if value else ""


def format_address(
    street: str,
    house_number: str,
    postcode: str,
    city: str,
    country: str,
    tags: dict[str, Any],
) -> str:
    if clean_tag(tags.get("addr:full")):
        return clean_tag(tags["addr:full"])

    parts = []
    street_line = " ".join(part for part in (street, house_number) if part)
    locality_line = " ".join(part for part in (postcode, city) if part)
    if street_line:
        parts.append(street_line)
    if locality_line:
        parts.append(locality_line)
    if country:
        parts.append(country)
    return ", ".join(parts)


def safe_sort_value(value: Any) -> str:
    return str(value or "").casefold()


if __name__ == "__main__":
    raise SystemExit(main())
