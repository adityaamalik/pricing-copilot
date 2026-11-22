"""Estimate price elasticities and save them for the app.

Run from the project root:  python -m src.build_pricing
"""
import pandas as pd

from src.forecast import prepare_sales
from src.pricing import estimate_elasticities, recommend_prices

sales = prepare_sales(pd.read_parquet("data/processed/sales_clean.parquet"))
descriptions = sales.groupby("stock_code")["description"].first().to_dict()

elasticities = estimate_elasticities(sales, descriptions)
elasticities.to_parquet("app_data/elasticities.parquet", index=False)

print(f"Products with an elasticity: {len(elasticities):,}")
recs = recommend_prices(elasticities)
print(recs["reason"].value_counts().to_string())
print(recs["decision"].value_counts().to_string())
print("Expected weekly margin change: GBP %.0f" % recs["margin_change"].sum())
print(recs.head(8)[["description", "current_price", "recommended_price", "elasticity",
                    "p_value", "margin_change"]].round(2).to_string())
