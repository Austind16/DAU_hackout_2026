"""
One-off script to seed Supabase from the society_140_full_dataset.csv /
house_info.csv files built earlier.

Usage:
    python scripts/seed_from_csv.py --house-info path/to/house_info.csv \
        --daily path/to/society_140_full_dataset.csv

Requires SUPABASE_URL / SUPABASE_KEY in the environment (.env).
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.database import get_supabase  # noqa: E402


def seed_users(house_info_path: str) -> dict:
    sb = get_supabase()
    id_map = {}  # house_id (H001...) -> supabase user uuid
    with open(house_info_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    payload = [
        {
            "owner_name": r["owner_name"],
            "block": r["block"],
            "flat_no": r["flat_no"],
            "family_size": int(r["family_size"]),
            "has_solar_panels": r["has_solar_panels"].lower() == "true",
            "panel_capacity_kw": float(r["panel_capacity_kW"] or 0),
            "panel_brand": r["panel_brand"] or None,
            "net_metering_status": r["net_metering_status"],
        }
        for r in rows
    ]

    res = sb.table("users").insert(payload).execute()
    for house_row, inserted in zip(rows, res.data):
        id_map[house_row["house_id"]] = inserted["id"]

    print(f"Inserted {len(res.data)} users.")
    return id_map


def seed_meter_readings(daily_csv_path: str, id_map: dict):
    sb = get_supabase()
    with open(daily_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    payload = []
    for r in rows:
        user_id = id_map.get(r["house_id"])
        if not user_id:
            continue
        payload.append({
            "user_id": user_id,
            "date": r["date"],
            "sunlight_hours": float(r["sunlight_hours"] or 0),
            "energy_produced_kwh": float(r["energy_produced_kWh"] or 0),
            "energy_consumed_kwh": float(r["energy_consumed_kWh"] or 0),
            "excess_power_kwh": float(r["excess_power_exported_kWh"] or 0),
            "grid_import_kwh": float(r["grid_import_kWh"] or 0),
        })

    # Insert in batches to stay under request size limits
    batch_size = 500
    total = 0
    for i in range(0, len(payload), batch_size):
        batch = payload[i:i + batch_size]
        res = sb.table("meter_readings").insert(batch).execute()
        total += len(res.data)
    print(f"Inserted {total} meter readings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--house-info", required=True)
    parser.add_argument("--daily", required=True)
    args = parser.parse_args()

    id_map = seed_users(args.house_info)
    seed_meter_readings(args.daily, id_map)
