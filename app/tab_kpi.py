"""Tab 1: KPI monitor."""
import plotly.graph_objects as go
import streamlit as st

from common import get_lang, load_table, t
from src.kpis import COST_SHARE, find_flags, get_kpis

# metric column -> number format for the big number
METRICS = {
    "revenue": "£{:,.0f}",
    "units": "{:,.0f}",
    "avg_price": "£{:.2f}",
    "margin_pct": "{:.1f}%",
    "return_rate": "{:.1f}%",
}


def make_chart(kpi, flags, metric):
    title = t("m_" + metric)
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


def show():
    weekly = load_table("weekly_kpis")
    st.subheader(t("kpi_question"))

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    countries = ["All"] + sorted(weekly["country"].unique())
    groups = ["All"] + sorted(weekly["product_group"].unique())
    country = col1.selectbox(t("country"), countries,
                             format_func=lambda x: t("all") if x == "All" else x)
    group = col2.selectbox(t("product_group"), groups,
                           format_func=lambda x: t("all") if x == "All" else t("grp_" + x))
    n_std = col3.slider(t("band_width"), 1.0, 3.0, 2.0, 0.5)
    wow_limit = col4.slider(t("wow_limit"), 10, 100, 50, 5) / 100

    kpi = get_kpis(weekly, country, group)
    flags = find_flags(kpi, n_std=n_std, wow_limit=wow_limit, lang=get_lang())

    # Big numbers: latest week vs. the week before
    latest, previous = kpi.iloc[-1], kpi.iloc[-2]
    cols = st.columns(len(METRICS))
    for col, (metric, fmt) in zip(cols, METRICS.items()):
        change = latest[metric] - previous[metric]
        col.metric(t("m_" + metric), fmt.format(latest[metric]), f"{change:+,.2f}")

    # Line charts, two per row
    metric_names = list(METRICS)
    for i in range(0, len(metric_names), 2):
        for col, metric in zip(st.columns(2), metric_names[i:i + 2]):
            col.plotly_chart(make_chart(kpi, flags, metric), width="stretch")

    # Flags table
    st.subheader(f"{t('flags_title')} ({len(flags)})")
    if len(flags) == 0:
        st.success(t("no_flags"))
    else:
        table = flags.copy()
        table["week"] = table["week"].dt.date
        table["metric"] = table["metric"].map(lambda m: t("m_" + m))
        table["change_vs_last_week"] = (table["change_vs_last_week"] * 100).round(1)
        table = table.round({"value": 2, "expected": 2})
        table.columns = [t("col_week"), t("col_metric"), t("col_value"),
                         t("col_expected"), t("col_change"), t("col_action")]
        st.dataframe(table, width="stretch", hide_index=True)

    st.caption(t("kpi_caption").format(share=f"{COST_SHARE:.0%}"))
