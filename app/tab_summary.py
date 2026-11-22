"""Tab 5: AI management summary."""
import streamlit as st

from common import load_table, t
from src.summary import (LANGUAGES, build_summary_input, cache_key, get_summary, load_cache,
                         make_client, make_prompt)


def find_api_key():
    """The key lives in Streamlit secrets (.streamlit/secrets.toml) or in an environment variable."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:          # no secrets file or no such key
        return None


def show_result(result):
    st.markdown(result["text"])
    if result["source"] == "llm":
        st.caption(t("ms_src_llm").format(model=result["model"]))
    elif result["source"] == "cache":
        st.caption(t("ms_src_cache").format(model=result["model"]))
    else:
        st.caption(t("ms_src_rules"))
    if result["error"]:
        st.warning(t("ms_error").format(error=result["error"]))


def show():
    data = build_summary_input(load_table("weekly_kpis"), load_table("rfm_customers"),
                               load_table("elasticities"), load_table("forecast_errors"),
                               load_table("forecast_future"))

    st.subheader(t("ms_question"))
    st.write(t("ms_intro"))

    refresh = st.checkbox(t("ms_refresh"))
    if st.button(t("ms_button"), type="primary"):
        client = make_client(find_api_key())
        with st.spinner(t("ms_working")):
            st.session_state["summaries"] = {
                lang: get_summary(data, lang, client=client, refresh=refresh) for lang in LANGUAGES}

    # Show the result of the button, or an already saved answer (no API call needed)
    summaries = st.session_state.get("summaries")
    if summaries is None:
        cache = load_cache()
        saved = {}
        for lang in LANGUAGES:
            system_prompt, user_prompt = make_prompt(data, lang)
            key = cache_key(lang, system_prompt, user_prompt)
            if key in cache:
                saved[lang] = {**cache[key], "source": "cache", "error": None}
        summaries = saved if len(saved) == len(LANGUAGES) else None

    if summaries is None:
        st.info(t("ms_no_summary"))
    else:
        col_en, col_de = st.columns(2)
        with col_en:
            st.markdown(f"### {t('ms_en')}")
            show_result(summaries["en"])
        with col_de:
            st.markdown(f"### {t('ms_de')}")
            show_result(summaries["de"])

    # Transparency: show exactly how the model is used
    with st.expander(t("ms_prompt_title")):
        st.markdown(t("ms_control"))
        system_prompt, user_prompt = make_prompt(data, "en")
        st.markdown(f"**{t('ms_system')}**")
        st.code(system_prompt, language="text")
        st.markdown(f"**{t('ms_user')}**")
        st.code(user_prompt, language="text")
