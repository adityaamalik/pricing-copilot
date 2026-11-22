"""Pricing Copilot - Streamlit app. Run from the project root:

    streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Let Python find the 'src' folder (it sits next to 'app')
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.kpis import COST_SHARE, find_flags, get_kpis  # noqa: E402

WEEKLY_FILE = ROOT / "data" / "processed" / "weekly_kpis.parquet"

# metric column -> (chart title, number format for the big number)
METRICS = {
    "revenue": ("Weekly revenue (GBP)", "£{:,.0f}"),
    "units": ("Weekly units", "{:,.0f}"),
    "avg_price": ("Average selling price (GBP)", "£{:.2f}"),
    "margin_pct": ("Estimated margin %", "{:.1f}%"),
    "return_rate": ("Return rate %", "{:.1f}%"),
}


@st.cache_data
def load_weekly():
    return pd.read_parquet(WEEKLY_FILE)


def make_chart(kpi, flags, metric):
    title = METRICS[metric][0]
    fig = go.Figure()
    fig.add_scatter(x=kpi["week"], y=kpi[metric], mode="lines", name=title)

    flagged = flags[flags["metric"] == metric]
    if len(flagged) > 0:
        points = kpi[kpi["week"].isin(flagged["week"])]
        fig.add_scatter(x=points["week"], y=points[metric], mode="markers",
                        name="Flag", marker=dict(color="red", size=9))

    fig.update_layout(title=title, height=300, showlegend=False,
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig


def show_kpi_tab(weekly):
    st.subheader("Is pricing on track?")

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    country = col1.selectbox("Country", ["All"] + sorted(weekly["country"].unique()))
    group = col2.selectbox("Product group", ["All"] + sorted(weekly["product_group"].unique()))
    n_std = col3.slider("Band width (± std deviations)", 1.0, 3.0, 2.0, 0.5)
    wow_limit = col4.slider("Week-over-week limit (%)", 10, 100, 50, 5) / 100

    kpi = get_kpis(weekly, country, group)
    flags = find_flags(kpi, n_std=n_std, wow_limit=wow_limit)

    # Big numbers: latest week vs. the week before
    latest, previous = kpi.iloc[-1], kpi.iloc[-2]
    cols = st.columns(len(METRICS))
    for col, (metric, (title, fmt)) in zip(cols, METRICS.items()):
        change = latest[metric] - previous[metric]
        col.metric(title, fmt.format(latest[metric]), f"{change:+,.2f}")

    # Line charts, two per row
    metric_names = list(METRICS)
    for i in range(0, len(metric_names), 2):
        for col, metric in zip(st.columns(2), metric_names[i:i + 2]):
            col.plotly_chart(make_chart(kpi, flags, metric), width="stretch")

    # Flags table
    st.subheader(f"Deviation flags ({len(flags)})")
    if len(flags) == 0:
        st.success("No deviations found for this selection.")
    else:
        table = flags.copy()
        table["week"] = table["week"].dt.date
        table["change_vs_last_week"] = (table["change_vs_last_week"] * 100).round(1)
        table = table.round({"value": 2, "expected": 2})
        st.dataframe(table, width="stretch", hide_index=True)

    st.caption(
        f"Assumption: there is no cost column, so unit cost is assumed to be "
        f"{COST_SHARE:.0%} of each product's median price. Margin is an estimate. "
        "Average price also moves with product mix, not only with price changes."
    )


st.set_page_config(page_title="Pricing Copilot", layout="wide")
st.title("Pricing Copilot")

weekly = load_weekly()
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["KPI monitor", "Customer segments", "Demand forecast", "Pricing engine", "Management summary"])

with tab1:
    show_kpi_tab(weekly)
with tab2:
    st.info("Coming in Block 3.")
with tab3:
    st.info("Coming in Block 4.")
with tab4:
    st.info("Coming in Block 5.")
with tab5:
    st.info("Coming in Block 6.")
