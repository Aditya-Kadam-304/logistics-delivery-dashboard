"""
01_clean_data.py

Cleans and standardizes the DataCo Smart Supply Chain dataset.
Download the raw CSV from Kaggle first and place it at data/raw/DataCoSupplyChainDataset.csv
https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis

Output: data/processed/shipments_clean.csv
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/DataCoSupplyChainDataset.csv")
OUTPUT_PATH = Path("data/processed/shipments_clean.csv")


def load_raw_data(path: Path) -> pd.DataFrame:
    # Dataset is known to have latin-1 encoding, not utf-8
    df = pd.read_csv(path, encoding="latin-1")
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    The raw dataset stores dates as text (e.g. '1/1/2018 0:00'). If saved to
    CSV and loaded into PostgreSQL as-is, pandas/SQLAlchemy will create the
    column as TEXT instead of TIMESTAMP, which silently breaks date functions
    like DATE_TRUNC() later in SQL. Converting explicitly here means the
    column keeps its real datetime type all the way through the pipeline.
    """
    date_cols = ["order_date_dateorders", "shipping_date_dateorders"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def define_late_delivery(df: pd.DataFrame) -> pd.DataFrame:
    """
    The dataset includes 'days_for_shipping_real' and 'days_for_shipment_scheduled'.
    A shipment is 'late' if actual shipping days exceed scheduled days.
    This is the single most important definition in the project — document it
    clearly in the README's Key Findings section once finalized.
    """
    df["is_late"] = (
        df["days_for_shipping_real"] > df["days_for_shipment_scheduled"]
    ).astype(int)
    df["delay_days"] = (
        df["days_for_shipping_real"] - df["days_for_shipment_scheduled"]
    ).clip(lower=0)
    return df


def select_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Trim to columns actually needed for the analysis — adjust as you explore
    keep_cols = [
        "order_id", "order_date_dateorders", "shipping_date_dateorders",
        "order_region", "order_country", "order_city",
        "market", "shipping_mode", "late_delivery_risk",
        "days_for_shipping_real", "days_for_shipment_scheduled",
        "is_late", "delay_days",
        "order_item_quantity", "sales", "category_name",
        "customer_segment", "department_name",
    ]
    available = [c for c in keep_cols if c in df.columns]
    missing = set(keep_cols) - set(available)
    if missing:
        print(f"Warning — columns not found in raw data: {missing}")
    return df[available]


def main():
    df = load_raw_data(RAW_PATH)
    df = standardize_columns(df)
    df = parse_dates(df)
    df = define_late_delivery(df)
    df = select_relevant_columns(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved cleaned data to {OUTPUT_PATH} ({len(df):,} rows)")
    print(f"Late delivery rate: {df['is_late'].mean():.1%}")


if __name__ == "__main__":
    main()
