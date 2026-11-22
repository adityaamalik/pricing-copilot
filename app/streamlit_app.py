"""Pricing Copilot - Streamlit app. Run from the project root:

    streamlit run app/streamlit_app.py
"""
import streamlit as st

import tab_kpi
import tab_segments
from common import t

st.set_page_config(page_title="Pricing Copilot", layout="wide")

# Language switch (the choice is remembered in st.session_state["lang"])
choice = st.sidebar.radio(t("language"), ["English", "Deutsch"])
st.session_state["lang"] = "de" if choice == "Deutsch" else "en"

st.title("Pricing Copilot")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [t("tab_kpi"), t("tab_segments"), t("tab_forecast"), t("tab_pricing"), t("tab_summary")])

with tab1:
    tab_kpi.show()
with tab2:
    tab_segments.show()
with tab3:
    st.info(t("coming_soon"))
with tab4:
    st.info(t("coming_soon"))
with tab5:
    st.info(t("coming_soon"))
