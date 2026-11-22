"""Tab 2: Customer segments (RFM)."""
import plotly.graph_objects as go
import streamlit as st

from common import load_table, t
from src.rfm import summarize_segments


def make_bar(summary, column, title):
    names = [t("seg_" + s) for s in summary["segment"]]
    fig = go.Figure(go.Bar(x=names, y=summary[column]))
    fig.update_layout(title=title, height=320, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def show():
    customers = load_table("rfm_customers")
    summary = summarize_segments(customers)

    st.subheader(t("seg_question"))

    # Two bar charts side by side
    col1, col2 = st.columns(2)
    col1.plotly_chart(make_bar(summary, "revenue_share_pct", t("chart_rev_share")), width="stretch")
    col2.plotly_chart(make_bar(summary, "customers", t("chart_customers")), width="stretch")

    # Segment table
    st.markdown(f"**{t('seg_table_title')}**")
    table = summary.copy()
    table["segment"] = table["segment"].map(lambda s: t("seg_" + s))
    table = table.round({"revenue": 0, "avg_recency_days": 0, "avg_orders": 1,
                         "revenue_share_pct": 1, "avg_price_paid": 2, "avg_discount_pct": 1})
    table.columns = [t("col_segment"), t("col_customers"), t("col_revenue"), t("col_recency"),
                     t("col_orders"), t("col_rev_share"), t("col_price_paid"), t("col_discount")]
    st.dataframe(table, width="stretch", hide_index=True)

    with st.expander(t("seg_rules_title")):
        st.markdown(t("seg_rules"))

    with st.expander(t("top_customers")):
        top = customers.sort_values("monetary", ascending=False).head(100).copy()
        top["segment"] = top["segment"].map(lambda s: t("seg_" + s))
        top = top[["customer_id", "country", "segment", "recency", "frequency", "monetary",
                   "r_score", "f_score", "m_score"]].round({"monetary": 0})
        st.dataframe(top, width="stretch", hide_index=True)

    st.caption(t("seg_caption"))
