"""Tab 3: Demand forecast."""
import plotly.graph_objects as go
import streamlit as st

from common import load_table, t


def make_chart(history, backtest, future):
    fig = go.Figure()
    fig.add_scatter(x=history["week"], y=history["units"], mode="lines",
                    name=t("fc_history"), line=dict(color="#444"))
    fig.add_scatter(x=backtest["week"], y=backtest["naive"], mode="lines",
                    name=t("fc_naive_bt"), line=dict(color="#e08a2c", dash="dot"))
    fig.add_scatter(x=backtest["week"], y=backtest["lgbm"], mode="lines",
                    name=t("fc_lgbm_bt"), line=dict(color="#1f77b4", dash="dot"))
    fig.add_scatter(x=future["week"], y=future["naive"], mode="lines+markers",
                    name=t("fc_naive_fc"), line=dict(color="#e08a2c"))
    fig.add_scatter(x=future["week"], y=future["lgbm"], mode="lines+markers",
                    name=t("fc_lgbm_fc"), line=dict(color="#1f77b4"))
    fig.update_layout(title=t("fc_chart_title"), height=420,
                      margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.15))
    return fig


def show():
    history = load_table("forecast_history")
    backtest = load_table("forecast_backtest")
    future = load_table("forecast_future")
    errors = load_table("forecast_errors")

    st.subheader(t("fc_question"))

    # Product picker (shows the description, keeps the code behind the scenes)
    names = dict(zip(errors["stock_code"], errors["description"]))
    code = st.selectbox(t("fc_product"), list(names), format_func=lambda c: f"{names[c]} ({c})")

    one = lambda table: table[table["stock_code"] == code]
    # Show the last 52 weeks of history so the forecast is easy to see
    recent = one(history).tail(52)
    st.plotly_chart(make_chart(recent, one(backtest), one(future)), width="stretch")

    # Error table, side by side
    st.markdown(f"**{t('fc_errors_title')}**")
    table = errors[["description", "mape_naive", "mape_lgbm"]].copy()
    average = {"description": t("fc_average"), "mape_naive": errors["mape_naive"].mean(),
               "mape_lgbm": errors["mape_lgbm"].mean()}
    table.loc[len(table)] = average
    table = table.round(1)
    table.columns = [t("fc_col_product"), t("fc_col_naive"), t("fc_col_lgbm")]
    st.dataframe(table, width="stretch", hide_index=True)

    wins = int((errors["mape_lgbm"] < errors["mape_naive"]).sum())
    st.success(t("fc_better").format(n=wins, total=len(errors)) + " "
               + t("fc_avg_text").format(naive=average["mape_naive"], lgbm=average["mape_lgbm"]))

    with st.expander(t("fc_how_title")):
        st.markdown(t("fc_how"))
    st.caption(t("fc_caption"))
