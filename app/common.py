"""Small helpers shared by all tabs."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Let Python find the 'src' folder (it sits next to 'app')
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from texts import TEXT  # noqa: E402


@st.cache_data
def load_table(name):
    """Read a small precomputed table from the app_data folder (cached)."""
    return pd.read_parquet(ROOT / "app_data" / f"{name}.parquet")


def get_lang():
    return st.session_state.get("lang", "en")


def t(key):
    """Text for the current language. Unknown keys are shown as they are."""
    return TEXT[get_lang()].get(key, key)
