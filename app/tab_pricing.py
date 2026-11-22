"""Tab 4: Pricing engine (elasticity + price recommendations)."""
import plotly.graph_objects as go
import streamlit as st

from common import load_table, t
from src.pricing import price_curve, recommend_prices


def make_curve_chart(row, recommended_price, max_change):
    curve = price_curve(row, max_change)
    current_margin = (row.current_price - row.unit_cost) * row.current_units_week
    new_margin = (recommended_price - row.unit_cost) * row.current_units_week * \
        (recommended_price / row.current_price) ** row.elasticity

    fig = go.Figure()
    fig.add_scatter(x=curve["price"], y=curve["margin"], mode="lines", name="margin")
    fig.add_scatter(x=[row.current_price], y=[current_margin], mode="markers",
                    name=t("pe_current"), marker=dict(size=12, color="#444"))
    fig.add_scatter(x=[recommended_price], y=[new_margin], mode="markers",
                    name=t("pe_recommended"), marker=dict(size=12, color="#1f77b4", symbol="diamond"))
    fig.update_layout(title=t("pe_detail_title"), xaxis_title=t("pe_curve_x"),
                      yaxis_title=t("pe_curve_y"), height=360, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def show():
    elasticities = load_table("elasticities")
    st.subheader(t("pe_question"))

    # Guardrails: change them and the recommendations are recalculated
    col1, col2, col3 = st.columns(3)
    max_change = col1.slider(t("pe_max_change"), 1, 20, 10) / 100
    min_margin = col2.slider(t("pe_min_margin"), 0, 50, 25) / 100
    alpha = col3.selectbox(t("pe_alpha"), [0.01, 0.05, 0.10], index=1)

    recs = recommend_prices(elasticities, max_change, min_margin, alpha)

    # Headline numbers
    cols = st.columns(5)
    cols[0].metric(t("pe_products"), f"{len(recs):,}")
    cols[1].metric(t("pe_raise"), f"{(recs['decision'] == 'raise').sum():,}")
    cols[2].metric(t("pe_lower"), f"{(recs['decision'] == 'lower').sum():,}")
    cols[3].metric(t("pe_revenue"), f"£{recs['revenue_change'].sum():+,.0f}")
    cols[4].metric(t("pe_margin"), f"£{recs['margin_change'].sum():+,.0f}")

    # Filters for the table
    col1, col2 = st.columns([2, 1])
    shown = col1.multiselect(t("pe_decision"), ["raise", "lower", "keep"], default=["raise", "lower"],
                             format_func=lambda d: t("dec_" + d))
    search = col2.text_input(t("pe_search"))
    view = recs[recs["decision"].isin(shown)]
    if search:
        view = view[view["description"].str.contains(search, case=False, na=False)]

    # Recommendation table
    st.markdown(f"**{t('pe_table_title')}**")
    table = view.copy()
    table["ci"] = table.apply(lambda r: f"{r['ci_low']:.2f} / {r['ci_high']:.2f}", axis=1)
    table["decision"] = table["decision"].map(lambda d: t("dec_" + d))
    table["reason"] = table["reason"].map(lambda r: t("reason_" + r))
    table = table[["description", "current_price", "recommended_price", "price_change_pct",
                   "elasticity", "ci", "p_value", "units_change_pct", "revenue_change",
                   "margin_change", "decision", "reason"]]
    table = table.round({"current_price": 2, "recommended_price": 2, "price_change_pct": 0,
                         "elasticity": 2, "p_value": 4, "units_change_pct": 1,
                         "revenue_change": 1, "margin_change": 1})
    table.columns = [t("pe_col_product"), t("pe_col_current"), t("pe_col_new"), t("pe_col_change"),
                     t("pe_col_elasticity"), t("pe_col_ci"), t("pe_col_p"), t("pe_col_units"),
                     t("pe_col_revenue"), t("pe_col_margin"), t("pe_col_decision"), t("pe_col_reason")]
    st.dataframe(table, width="stretch", hide_index=True, height=380)

    # One product in detail: where is the best price?
    if len(view) > 0:
        names = dict(zip(view["stock_code"], view["description"]))
        code = st.selectbox(t("pe_pick_product"), list(names)[:200],
                            format_func=lambda c: f"{names[c]} ({c})")
        row = view[view["stock_code"] == code].iloc[0]
        st.plotly_chart(make_curve_chart(row, row["recommended_price"], max_change), width="stretch")

    with st.expander(t("pe_how_title")):
        st.markdown(t("pe_how"))
    st.caption(t("pe_caption"))
