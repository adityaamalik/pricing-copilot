# Pricing Copilot

A small Streamlit app on public retail data that **monitors pricing KPIs, segments customers, forecasts demand,
recommends price changes and writes a management summary in German and English** with an LLM.

**Live app:** _add the Streamlit Community Cloud link here after deploying_

> Built AI-first with Claude (Claude Code) as a pair programmer for planning, coding, testing and documentation.
> Every method choice and assumption below was reviewed by me.

## What it does (five tabs, each answers one management question)

| Tab | Question | Method |
| --- | --- | --- |
| 1. KPI monitor | Is pricing on track? | Weekly revenue, units, average price, estimated margin, return rate. A week is flagged if it is outside its rolling mean ± 2 standard deviations or moves more than a set % vs. last week. Each flag gets a rule-based suggested action. |
| 2. Customer segments | Who buys, and how price-sensitive are they? | RFM scoring (Recency, Frequency, Monetary, 1-5) and named segments: Champions, Loyal, New, At risk, Hibernating. Per segment: customers, revenue share, average price paid, average discount. |
| 3. Demand forecast | What will we sell next? | 8-week forecast for the top 10 products. LightGBM (direct multi-step) vs. a seasonal-naive baseline, compared in a 12-week backtest (MAPE). |
| 4. Pricing engine | Which prices should change? | Log-log price elasticity per product (robust standard errors, p-value, confidence interval). A recommender tests prices within ±10% of today's, picks the highest expected margin, inside guardrails (max change, minimum margin, significance). Guardrails are sliders. |
| 5. Management summary | What should we decide this week? | An LLM (Claude) writes a one-page summary (3 findings, 3 actions, risks) in German and English from the numbers of tabs 1-4. The prompt and data are shown in the app. |

The app has a German / English switch.

## Data

[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii): about 1.07 million transactions of a
UK online retailer (Dec 2009 - Dec 2011), CC BY 4.0. Many customers are small businesses buying in bulk.

Cleaning: cancellations and returns (negative quantity) are removed from sales, as are zero prices and non-product
codes (postage, bank charges, ...). Rows without a customer ID are kept for KPIs but not for RFM.

## Assumptions and limitations (please read)

- **Margin is estimated.** The data has no cost column, so unit cost is assumed to be **60% of the product's median price**.
- **Elasticities are indicative, not causal.** They come from historical prices and sales. Bulk order lines (over 100 units)
  carry volume discounts and are excluded from the price measure; store-wide weekly demand is a control for seasonality.
  Over 1,500 products are tested, so some "significant" results are chance. Expected effects assume a constant elasticity.
- **Forecasts are uncertain.** Weekly sales per product are lumpy (wholesale orders): average backtest error is
  about 56% (LightGBM) vs. 82% (seasonal naive). LightGBM wins for 6 of 10 products, not all. With two years of data
  the yearly pattern is learned from a single previous year.
- **Average selling price moves with product mix**, not only with price changes.
- **KPI flags are noisy in seasonal peaks** because a rolling band does not know about seasonality.
  A better method (compare to the same week last year) is a next step.
- The LLM only sees the aggregated JSON shown in the app. A person should read the summary before acting on it.

## Run it yourself

```bash
git clone https://github.com/adityaamalik/pricing-copilot.git
cd pricing-copilot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt        # on macOS LightGBM also needs:  brew install libomp
streamlit run app/streamlit_app.py         # the small tables the app reads are in app_data/
```

Rebuild everything from the raw data:

```bash
# 1. download online_retail_II.xlsx from the UCI link above into data/raw/
python -m src.prepare_data                 # clean the raw file -> data/processed/*.parquet
./build_all.sh                             # weekly KPIs, RFM, forecast, elasticities -> app_data/
python -m pytest                           # tests
```

AI summary (optional): copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add an Anthropic API key,
or run `export ANTHROPIC_API_KEY=...` and `python -m src.build_summary` to save the German and English summaries in
`app_data/summary_cache.json`. Without a key the tab shows a rule-based text instead.

## Project structure

```
app/          Streamlit app: streamlit_app.py (entry), one tab_*.py per tab, texts.py (EN + DE texts)
src/          All logic: cleaning, kpis, rfm, forecast, pricing, summary, and build_*.py scripts
app_data/     Small precomputed tables the deployed app reads
tests/        pytest tests for every module
```

## Next steps

- Compare each week with the same week last year in the KPI monitor (seasonality-aware flags).
- Price elasticity per customer segment, and a hierarchical model that shares information between similar products.
- Replace the assumed cost with real cost data; add competitor prices.
- Test recommended price changes in a controlled experiment before rolling them out.
