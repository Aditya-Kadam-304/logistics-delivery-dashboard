"""
02_weather_pull.py

Pulls current weather data for major shipping hub regions and appends it
to data/processed/weather_log.csv. Designed to run daily via GitHub Actions
(.github/workflows/weather_pull.yml) so the dataset grows into a genuine
time series over the life of the project.

Requires OPENWEATHER_API_KEY in .env (or as a GitHub Actions secret).
"""

import os
import csv
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
OUTPUT_PATH = Path("data/processed/weather_log.csv")

# Adjust to match the top regions/cities present in your cleaned dataset
HUB_LOCATIONS = {
    "Los Angeles": (34.0522, -118.2437),
    "New York": (40.7128, -74.0060),
    "Chicago": (41.8781, -87.6298),
    "Frankfurt": (50.1109, 8.6821),
    "Rotterdam": (51.9244, 4.4777),
    "Singapore": (1.3521, 103.8198),
}

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str, lat: float, lon: float) -> dict:
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
        "city": city,
        "temp_c": data["main"]["temp"],
        "condition": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "wind_speed_ms": data["wind"]["speed"],
        "humidity_pct": data["main"]["humidity"],
    }


def append_to_log(rows: list[dict], path: Path):
    file_exists = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    if not API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set — check your .env file or GitHub secret")

    rows = []
    for city, (lat, lon) in HUB_LOCATIONS.items():
        try:
            rows.append(fetch_weather(city, lat, lon))
            print(f"Fetched weather for {city}")
        except requests.RequestException as e:
            print(f"Failed to fetch weather for {city}: {e}")

    if rows:
        append_to_log(rows, OUTPUT_PATH)
        print(f"Appended {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
