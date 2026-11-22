"""Run the forecast and the backtest, and save the results for the app.

Run from the project root:  python -m src.build_forecast
"""
import pandas as pd

from src.forecast import (pick_top_products, prepare_sales, run_backtest,
                          run_forecast, mape_table, weekly_units)

sales = prepare_sales(pd.read_parquet("data/processed/sales_clean.parquet"))

top = pick_top_products(sales)
units = weekly_units(sales, top.index)
descriptions = top["description"].to_dict()

backtest = run_backtest(units)
future = run_forecast(units)
errors = mape_table(backtest, descriptions)

# History in long format (week, product, units) for the chart
history = units.reset_index(names="week").melt(id_vars="week", var_name="stock_code",
                                               value_name="units")
for table in (history, backtest, future):
    table["description"] = table["stock_code"].map(descriptions)

history.to_parquet("app_data/forecast_history.parquet", index=False)
backtest.to_parquet("app_data/forecast_backtest.parquet", index=False)
future.to_parquet("app_data/forecast_future.parquet", index=False)
errors.to_parquet("app_data/forecast_errors.parquet", index=False)

print(errors.round(1).to_string())
print("Average error (MAPE): baseline %.1f%%, LightGBM %.1f%%"
      % (errors["mape_naive"].mean(), errors["mape_lgbm"].mean()))
print("Forecast weeks:", future["week"].min().date(), "->", future["week"].max().date())
