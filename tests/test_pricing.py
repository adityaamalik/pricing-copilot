import numpy as np
import pandas as pd
import pytest

from src.pricing import best_price, fit_elasticity, recommend_prices


def test_fit_elasticity_finds_the_true_value_in_made_up_data():
    rng = np.random.default_rng(1)
    price = rng.uniform(0.8, 1.2, 80)
    store = rng.uniform(900, 1100, 80)
    units = 500 * price ** -2.0 * (store / 1000) * rng.normal(1, 0.05, 80)   # true elasticity = -2
    data = pd.DataFrame({"list_price": price, "store_units": store, "units": units})
    result = fit_elasticity(data)
    assert result["elasticity"] == pytest.approx(-2.0, abs=0.3)
    assert result["p_value"] < 0.05


def test_elastic_product_gets_a_price_cut():
    # cost 0.6, price 1.0, elasticity -3 -> best price is 0.6 * 3 / 2 = 0.90 (-10%)
    change = best_price(1.0, 100, 0.6, -3.0, max_change=0.20, min_margin=0.0)
    assert change == pytest.approx(-0.10)


def test_inelastic_product_gets_a_price_rise_up_to_the_limit():
    change = best_price(1.0, 100, 0.6, -0.5, max_change=0.10, min_margin=0.0)
    assert change == pytest.approx(0.10)


def test_minimum_margin_guardrail_blocks_price_cuts():
    # Without the guardrail the best change is -4%, but that would leave a margin below 25%
    assert best_price(1.0, 100, 0.8, -6.0, 0.10, min_margin=0.0) == pytest.approx(-0.04)
    assert best_price(1.0, 100, 0.8, -6.0, 0.10, min_margin=0.25) == 0.0


def test_no_change_when_elasticity_is_not_significant():
    table = pd.DataFrame({
        "stock_code": ["A", "B"], "description": ["a", "b"],
        "elasticity": [-2.0, -2.0], "p_value": [0.50, 0.001],
        "current_price": [1.0, 1.0], "current_units_week": [100.0, 100.0], "unit_cost": [0.6, 0.6],
    })
    result = recommend_prices(table).set_index("stock_code")
    assert result.loc["A", "price_change_pct"] == 0
    assert result.loc["A", "reason"] == "not_significant"
    assert result.loc["B", "price_change_pct"] != 0
