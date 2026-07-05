"""
03_load_to_postgres.py

Loads the cleaned shipment data and the weather log into PostgreSQL.
Run sql/schema.sql first to create the tables — this script assumes the
tables already exist with the correct column types (TIMESTAMP, NUMERIC,
etc.) and only truncates + inserts data, rather than letting pandas
recreate the tables from scratch. Recreating via pandas' if_exists="replace"
infers types from the dataframe, which turns date columns into TEXT and
silently breaks SQL functions like DATE_TRUNC() later on.
"""

from pathlib import Path
import pandas as pd
from sqlalchemy import text
from db_config import get_engine

SHIPMENTS_PATH = Path("data/processed/shipments_clean.csv")
WEATHER_PATH = Path("data/processed/weather_log.csv")

# Columns that must be parsed as real datetimes, not text, before loading
DATE_COLUMNS = {
    "shipments": ["order_date_dateorders", "shipping_date_dateorders"],
    "weather_log": ["pulled_at_utc"],
}


def load_table(csv_path: Path, table_name: str, engine, truncate_first: bool):
    if not csv_path.exists():
        print(f"Skipping {table_name} — {csv_path} not found yet")
        return

    df = pd.read_csv(csv_path)

    for col in DATE_COLUMNS.get(table_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if truncate_first:
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))

    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"Loaded {len(df):,} rows into '{table_name}'")


def main():
    engine = get_engine()
    # Shipments is a full historical reload each run — truncate then reload
    load_table(SHIPMENTS_PATH, "shipments", engine, truncate_first=True)
    # Weather log grows daily — never truncate, just append new rows
    load_table(WEATHER_PATH, "weather_log", engine, truncate_first=False)


if __name__ == "__main__":
    main()
