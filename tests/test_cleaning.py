import pandas as pd
import pytest

from src.cleaning import clean_sales


def make_sample():
    """Six fake rows: 2 good sales and 4 rows that must be removed."""
    return pd.DataFrame({
        "invoice":     ["500001", "C500002", "500003", "500004", "500005", "500006"],
        "stock_code":  ["85123A", "85123A",  "22423",  "POST",   "22423",  "21232"],
        "description": ["HEART",  "HEART",   "CAKESTAND", "POSTAGE", "CAKESTAND", "MUG"],
        "quantity":    [6,        -6,        -2,       1,        4,        10],
        "price":       [2.55,     2.55,      12.75,    18.00,    0.00,     1.25],
        "customer_id": [17850.0,  17850.0,   13047.0,  12583.0,  13047.0,  None],
        "country":     ["United Kingdom"] * 6,
    })
    # row 0: good | row 1: cancellation | row 2: return | row 3: postage fee
    # row 4: zero price | row 5: good, but no customer ID


def test_removes_cancellations_and_returns():
    result = clean_sales(make_sample())
    assert not result["invoice"].str.startswith("C").any()
    assert (result["quantity"] > 0).all()


def test_removes_zero_prices_and_fee_codes():
    result = clean_sales(make_sample())
    assert (result["price"] > 0).all()
    assert not result["stock_code"].isin(["POST"]).any()


def test_keeps_good_rows_and_adds_revenue():
    result = clean_sales(make_sample())
    assert len(result) == 2
    assert result["customer_id"].isna().sum() == 1   # missing customer ID is kept
    assert result["revenue"].iloc[0] == pytest.approx(6 * 2.55)