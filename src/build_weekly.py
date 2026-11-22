"""Build the small weekly KPI table the app reads.

Run from the project root:  python -m src.build_weekly
"""
import pandas as pd

from src.cleaning import clean_returns
from src.kpis import build_weekly_table

RAW = "data/processed/transactions_raw.parquet"
SALES = "data/processed/sales_clean.parquet"
OUT = "data/processed/weekly_kpis.parquet"

raw = pd.read_parquet(RAW)
returns = clean_returns(raw)
sales = pd.read_parquet(SALES)

weekly = build_weekly_table(sales, returns)
weekly.to_parquet(OUT, index=False)
print(f"Saved {len(weekly):,} rows to {OUT}")
print(f"Weeks: {weekly['week'].min().date()} -> {weekly['week'].max().date()}")
print(weekly["product_group"].value_counts())
