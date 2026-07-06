"""
05_historical_weather_pull.py

Pulls REAL historical daily weather (precipitation, temperature, weather
condition code) for each geocoded city, covering the full date range
present in the shipment data. Uses Open-Meteo's free Historical Weather
API — no key required, and one API call retrieves an entire date range
for a location, so this is efficient even across a multi-year dataset.

This is what makes the weather-to-delivery correlation genuinely valid:
each row of weather data corresponds to a real date, matchable to the
real order_date_dateorders in your shipments table — unlike the daily
GitHub Actions pull (02_weather_pull.py), which only ever captures
"today," and can't be joined to historical orders.

Requires: data/processed/top_cities_geocoded.csv (run 04_geocode_top_cities.py first)
Output: data/processed/historical_weather.csv
"""

import time
from pathlib import Path

import pandas as pd
import requests

CITIES_PATH = Path("data/processed/top_cities_geocoded.csv")
SHIPMENTS_PATH = Path("data/processed/shipments_clean.csv")
OUTPUT_PATH = Path("data/processed/historical_weather.csv")

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# WMO weather codes (used by Open-Meteo) collapsed into simple categories,
# so the eventual dashboard chart has a handful of readable buckets instead
# of ~30 granular codes.
WEATHER_CODE_GROUPS = {
    range(0, 2): "Clear",
    range(2, 4): "Cloudy",
    range(45, 49): "Fog",
    range(51, 68): "Rain",
    range(71, 78): "Snow",
    range(80, 100): "Storm",
}


def simplify_weather_code(code: int) -> str:
    for code_range, label in WEATHER_CODE_GROUPS.items():
        if code in code_range:
            return label
    return "Other"


def get_date_range(shipments_path: Path) -> tuple[str, str]:
    df = pd.read_csv(shipments_path, usecols=["order_date_dateorders"])
    dates = pd.to_datetime(df["order_date_dateorders"], errors="coerce")
    return dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")


def fetch_historical_weather(city: str, lat: float, lon: float, start: str, end: str) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "precipitation_sum,temperature_2m_mean,weathercode",
        "timezone": "auto",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()["daily"]

    df = pd.DataFrame({
        "order_city": city,
        "date": data["time"],
        "precipitation_mm": data["precipitation_sum"],
        "temp_mean_c": data["temperature_2m_mean"],
        "weather_code": data["weathercode"],
    })
    df["weather_condition"] = df["weather_code"].apply(simplify_weather_code)
    return df


def main():
    if not CITIES_PATH.exists():
        raise FileNotFoundError(
            f"{CITIES_PATH} not found — run scripts/04_geocode_top_cities.py first"
        )

    cities = pd.read_csv(CITIES_PATH)
    start_date, end_date = get_date_range(SHIPMENTS_PATH)
    print(f"Pulling historical weather from {start_date} to {end_date} "
          f"for {len(cities)} cities...")

    all_weather = []
    for _, row in cities.iterrows():
        city = row["order_city"]
        try:
            weather_df = fetch_historical_weather(
                city, row["latitude"], row["longitude"], start_date, end_date
            )
            all_weather.append(weather_df)
            print(f"Fetched {len(weather_df)} days of weather for '{city}'")
        except requests.RequestException as e:
            print(f"Failed to fetch weather for '{city}': {e}")

        time.sleep(1)  # be polite to the free API

    if not all_weather:
        print("No weather data fetched — check top_cities_geocoded.csv")
        return

    combined = pd.concat(all_weather, ignore_index=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(combined):,} total city-day weather records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
