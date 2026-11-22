import pandas as pd
import pytest

from src.kpis import add_ratios, find_flags, get_product_group, suggest_action


def test_product_group_uses_keywords():
    assert get_product_group("PINK CHRISTMAS MUG") == "Christmas"   # Christmas wins over Kitchen
    assert get_product_group("RED SHOPPER BAG") == "Bags"
    assert get_product_group("SOMETHING ELSE") == "Other"


def test_ratios_are_computed_from_sums():
    kpi = pd.DataFrame({"revenue": [100.0], "units": [50.0],
                        "cost": [60.0], "returns_revenue": [5.0]})
    kpi = add_ratios(kpi)
    assert kpi["avg_price"][0] == pytest.approx(2.0)
    assert kpi["margin_pct"][0] == pytest.approx(40.0)
    assert kpi["return_rate"][0] == pytest.approx(5.0)


def test_flag_found_for_a_sudden_spike():
    weeks = pd.date_range("2011-01-03", periods=12, freq="W-MON")
    revenue = [100.0] * 11 + [300.0]                     # last week triples
    kpi = pd.DataFrame({"week": weeks, "revenue": revenue, "units": 50.0,
                        "avg_price": 2.0, "margin_pct": 40.0})
    flags = find_flags(kpi)
    assert (flags["metric"] == "revenue").any()
    assert flags["week"].iloc[0] == weeks[-1]            # newest flag is listed first


def test_action_text_for_price_up_units_down():
    text = suggest_action(price_change=0.08, units_change=-0.20, metric="units", is_high=False)
    assert "review prices" in text
