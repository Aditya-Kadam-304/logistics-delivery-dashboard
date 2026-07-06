"""
04_geocode_top_cities.py

Identifies the highest-volume order cities in the cleaned shipment data,
then looks up their latitude/longitude using Open-Meteo's free Geocoding
API (no key required). This is the first step toward pulling REAL
historical weather matched to actual shipment dates — unlike
02_weather_pull.py, which only captures today's weather and can't be
matched to historical orders.

Output: data/processed/top_cities_geocoded.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

INPUT_PATH = Path("data/processed/shipments_clean.csv")
OUTPUT_PATH = Path("data/processed/top_cities_geocoded.csv")

TOP_N_CITIES = 10  # keep this small — each city costs one weather API call later
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_top_cities(df: pd.DataFrame, n: int) -> pd.DataFrame:
    counts = (
        df["order_city"]
        .value_counts()
        .head(n)
        .reset_index()
    )
    counts.columns = ["order_city", "shipment_count"]
    return counts


def geocode_city(city: str) -> dict | None:
    params = {"name": city, "count": 1}
    response = requests.get(GEOCODE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        return None

    result = data["results"][0]
    return {
        "matched_name": result.get("name"),
        "country": result.get("country"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
    }


def main():
    df = pd.read_csv(INPUT_PATH)
    top_cities = get_top_cities(df, TOP_N_CITIES)

    geocoded_rows = []
    for _, row in top_cities.iterrows():
        city = row["order_city"]
        try:
            geo = geocode_city(city)
            if geo:
                geocoded_rows.append({
                    "order_city": city,
                    "shipment_count": row["shipment_count"],
                    **geo,
                })
                print(f"Geocoded '{city}' -> {geo['matched_name']}, {geo['country']}")
            else:
                print(f"No geocoding match found for '{city}' — skipping")
        except requests.RequestException as e:
            print(f"Failed to geocode '{city}': {e}")

        time.sleep(1)  # be polite to the free API — avoid rate limiting

    result_df = pd.DataFrame(geocoded_rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(result_df)} geocoded cities to {OUTPUT_PATH}")
    print("Review this file before continuing — drop any obviously wrong matches"
          " (e.g. a common city name matched to the wrong country) by editing the CSV.")


if __name__ == "__main__":
    main()
