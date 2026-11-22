"""Generate the management summary (English + German) with Claude and save it in the cache.

Needs an API key:   export ANTHROPIC_API_KEY="sk-ant-..."
Run from the project root:  python -m src.build_summary
Then commit app_data/summary_cache.json so the deployed app shows the summary instantly.
"""
import sys

import pandas as pd

from src.summary import build_summary_input, get_summary, make_client

client = make_client()
if client is None:
    sys.exit("No API key found. Run:  export ANTHROPIC_API_KEY='your-key'  and try again.")

data = build_summary_input(
    pd.read_parquet("app_data/weekly_kpis.parquet"),
    pd.read_parquet("app_data/rfm_customers.parquet"),
    pd.read_parquet("app_data/elasticities.parquet"),
    pd.read_parquet("app_data/forecast_errors.parquet"),
    pd.read_parquet("app_data/forecast_future.parquet"),
)

for language in ("en", "de"):
    result = get_summary(data, language, client=client, refresh=True)
    print(f"--- {language} (source: {result['source']}) ---")
    print(result["text"], "\n")
    if result["error"]:
        print("Problem:", result["error"])
