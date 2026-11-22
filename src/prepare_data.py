"""Read the raw Excel once, clean it, and save fast Parquet files.

Run from the project root:  python -m src.prepare_data
"""
from pathlib import Path

import pandas as pd

from src.cleaning import clean_sales

RAW_EXCEL = Path("data/raw/online_retail_II.xlsx")
RAW_PARQUET = Path("data/processed/transactions_raw.parquet")
CLEAN_PARQUET = Path("data/processed/sales_clean.parquet")

# Excel column names have spaces and capitals -> rename to simple snake_case
COLUMN_NAMES = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def load_raw_excel(path):
    # sheet_name=None reads EVERY sheet and returns {sheet name: DataFrame}
    sheets = pd.read_excel(path, sheet_name=None)
    print("Sheets found:", list(sheets.keys()))

    # Stack the two years on top of each other
    df = pd.concat(sheets.values(), ignore_index=True)
    df = df.rename(columns=COLUMN_NAMES)

    # Some columns mix numbers and text (invoice 489434 vs "C489449").
    # Parquet needs one type per column, so store these as text.
    for col in ["invoice", "stock_code", "description"]:
        df[col] = df[col].astype("string")
    return df


def main():
    print("Reading Excel (this takes a few minutes)...")
    raw = load_raw_excel(RAW_EXCEL)

    RAW_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    raw.to_parquet(RAW_PARQUET, index=False)
    print(f"Raw rows:   {len(raw):,}")

    sales = clean_sales(raw)
    sales.to_parquet(CLEAN_PARQUET, index=False)
    print(f"Clean rows: {len(sales):,}  (removed {len(raw) - len(sales):,})")
    print(f"Dates: {sales['invoice_date'].min()} -> {sales['invoice_date'].max()}")


if __name__ == "__main__":
    main()