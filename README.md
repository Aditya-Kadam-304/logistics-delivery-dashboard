# Delivery Performance & Delay Risk Dashboard

**Business question:** Which factors (region, carrier, weather, order size) drive late deliveries, and can we flag high-risk shipments before they ship?

## Overview

This project analyzes ~180K historical shipment records to identify drivers of delivery delays, then enriches that analysis with live weather data pulled daily via an automated pipeline. The end deliverable is a Power BI dashboard that a logistics operations manager could actually use to spot risk before it becomes a customer complaint.

## Why this project

Most analytics portfolios stop at a static Kaggle dashboard. This one adds two things real analyst work requires:
- **A live data pipeline** — weather data is pulled automatically every day via GitHub Actions and appended to the database, not downloaded once and forgotten.
- **A defined business decision** — the output isn't just charts, it's a risk score that flags which upcoming shipments are more likely to be late.

## Data Sources

| Source | Type | Purpose |
|---|---|---|
| [DataCo Smart Supply Chain Dataset](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) | Static, ~180K rows | Historical order/shipment/delivery records |
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) | Historical, matched to actual order dates | Real weather-to-delivery correlation for top 10 shipping cities |
| [OpenWeatherMap API](https://openweathermap.org/api) | Live, daily pull via GitHub Actions | Separate live-monitoring automation demo (see note below) |

**Important note on the two weather sources:** early in this project, a daily
OpenWeatherMap pull (automated via GitHub Actions) was used with the
intention of correlating weather with delivery delays. That doesn't
actually work — OpenWeatherMap's free tier only returns *today's* weather,
which can't be matched to shipments from 2015-2018. The real
weather-to-delivery correlation instead uses **Open-Meteo's free Historical
Weather API**, which returns real past daily weather for any date —
correctly matched to each shipment's actual order date. The OpenWeatherMap
automation is kept in the project as a separate, standalone demonstration
of building an automated daily data pipeline (see
`docs/GITHUB_ACTIONS_SETUP.md`), but it is not used in any of the delay
analysis.

## Tech Stack

- **Python** — data cleaning, API pipeline, PostgreSQL loading
- **PostgreSQL** — central database for cleaned + enriched data
- **SQL** — analysis queries (delay rates, risk scoring, trends)
- **Power BI** — final interactive dashboard
- **Excel** — supplementary carrier scorecard (pivot-table based)
- **GitHub Actions** — daily automated weather pull

## Project Structure

```
logistics-delivery-dashboard/
├── data/
│   ├── raw/                  # Original Kaggle CSV (not committed — see .gitignore)
│   └── processed/            # Cleaned data ready for DB load
├── scripts/
│   ├── 01_clean_data.py      # Cleans and standardizes the Kaggle dataset
│   ├── 02_weather_pull.py    # Live daily pull (automation demo only — see note above)
│   ├── 03_load_to_postgres.py # Loads all data into PostgreSQL
│   ├── 04_geocode_top_cities.py    # Finds + geocodes top 10 shipping cities
│   ├── 05_historical_weather_pull.py # Pulls REAL historical weather for those cities
│   └── db_config.py          # DB connection helper (reads from .env)
├── sql/
│   ├── schema.sql            # Table definitions
│   └── analysis_queries.sql  # Delay rate, risk scoring, trend queries
├── .github/workflows/
│   └── weather_pull.yml      # Daily automation — runs 02_weather_pull.py
├── excel/
│   └── carrier_scorecard.xlsx # (to be added in Week 3)
├── powerbi/
│   └── delivery_dashboard.pbix # (to be added in Week 3)
├── .env.example
├── requirements.txt
└── README.md
```

## Roadmap

- [ ] **Week 1** — Data cleaning + exploration, define "late delivery" and risk metrics precisely
- [ ] **Week 2** — Build + automate weather API pipeline, merge with historical data
- [ ] **Week 3** — SQL analysis layer + Power BI dashboard build + Excel scorecard
- [ ] **Week 4** — Polish, write findings/recommendations, record walkthrough, publish

## Key Findings

*(Based on the DataCo dataset, 180,519 shipments)*

- **Overall on-time rate is 42.7%** (57.3% of shipments are late) — a substantial, business-relevant problem, not a marginal one.
- **Shipping mode drives lateness far more than region does.** Late rates by region cluster tightly between 52-61% (a ~9 point spread), while late rates by shipping mode range from 39.8% to 100% — a much larger and more actionable signal.
- **First Class shipments show a 100% late rate — but this is an SLA design issue, not an operational failure.** Investigation into the underlying data showed all 27,814 First Class orders are scheduled for 1-day delivery but consistently take 2 days, with zero variance across every single order. The fulfillment process is completely consistent; the promised delivery window is simply shorter than the process can achieve. This is a stronger, more useful finding than the raw percentage alone — it points to renegotiating the SLA rather than fixing a broken process.
- **Standard Class (the highest-volume tier at 107,752 orders) has the best relative on-time performance** at 39.8% late, suggesting the core fulfillment process works reasonably well when given a realistic delivery window.
- **Highest risk combination:** Second Class shipments to Central Asia (90.6% late, risk score 70.1) — this is the top actionable target once First Class's SLA issue is separately addressed, since it reflects genuine operational delay rather than a scheduling artifact.
- **July 2016 shows an apparent dip in late deliveries (55.2% vs. ~57-59% in surrounding months) — but this is a data collection gap, not a real improvement.** Investigating further showed every region except four US regions (US Center, East of USA, West of USA, South of USA) had zero shipments recorded that month, compared to normal volume in June and August. The apparent "improvement" is an artifact of international data being missing for that month, not a genuine operational win — a good example of not taking a promising number at face value before drawing a conclusion.
- **Weather genuinely correlates with delivery delays, for the top 10 shipping cities analyzed.** Using real historical weather matched to actual shipment dates (see Data Sources), late rate rises consistently from Clear (54.2%) → Cloudy (56.5%) → Rain (57.9%) → Snow (69.0%). The Rain vs. Clear comparison (7,772 vs. 1,361 shipments) is statistically solid; the Snow figure is based on only 29 shipments and should be treated as a smaller, less certain signal despite the striking number.

**Recommendation:** Prioritize renegotiating the First Class SLA (either extend the promised window to 2 days, or invest in genuinely faster fulfillment) before over-indexing on region-level interventions, which show far less variation.

## Setup

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Fill in your OpenWeatherMap API key and PostgreSQL credentials

# 3. Download the raw dataset from Kaggle into data/raw/

# 4. Run the pipeline
python scripts/01_clean_data.py
python scripts/04_geocode_top_cities.py
python scripts/05_historical_weather_pull.py
python scripts/03_load_to_postgres.py
```

## Author

Aditya Kadam — [LinkedIn](https://linkedin.com/in/theadityakadam) | [GitHub](https://github.com/Aditya-Kadam-304)
