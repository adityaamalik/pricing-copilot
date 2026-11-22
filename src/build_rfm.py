"""Build the RFM customer table the app reads.

Run from the project root:  python -m src.build_rfm
"""
import pandas as pd

from src.rfm import calculate_rfm, summarize_segments

SALES = "data/processed/sales_clean.parquet"
OUT = "app_data/rfm_customers.parquet"

sales = pd.read_parquet(SALES)
customers = calculate_rfm(sales)
customers.to_parquet(OUT, index=False)

print(f"Saved {len(customers):,} customers to {OUT}")
print(summarize_segments(customers).round(1).to_string())
