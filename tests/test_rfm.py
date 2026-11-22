import pandas as pd
import pytest

from src.rfm import calculate_rfm, make_score, name_segment, summarize_segments


def make_sales():
    """Three customers plus one row without a customer ID."""
    return pd.DataFrame({
        "invoice":      ["1", "2", "3", "4", "5"],
        "invoice_date": pd.to_datetime(["2011-01-01", "2011-12-01", "2011-12-08",
                                        "2011-06-01", "2011-12-05"]),
        "stock_code":   ["A", "A", "A", "A", "A"],
        "quantity":     [10, 10, 10, 10, 10],
        "price":        [2.0, 2.0, 1.0, 2.0, 2.0],
        "revenue":      [20.0, 20.0, 10.0, 20.0, 20.0],
        "customer_id":  [1.0, 1.0, 2.0, 3.0, None],
        "country":      ["United Kingdom"] * 5,
    })


def test_scores_are_between_1_and_5_and_ties_are_equal():
    scores = make_score(pd.Series([1, 1, 1, 50, 100]))
    assert scores.min() >= 1 and scores.max() <= 5
    assert scores[0] == scores[1] == scores[2]       # same value -> same score
    assert scores[4] == 5                            # the biggest value gets a 5


def test_recency_score_is_reversed():
    # fewer days since last order = better = higher score
    scores = make_score(pd.Series([1, 100, 200]), higher_is_better=False)
    assert scores[0] > scores[2]


def test_segment_names():
    assert name_segment(5, 5) == "Champions"
    assert name_segment(3, 3) == "Loyal"
    assert name_segment(5, 1) == "New"
    assert name_segment(1, 5) == "At risk"
    assert name_segment(1, 1) == "Hibernating"


def test_customers_without_id_are_left_out_and_numbers_are_right():
    customers = calculate_rfm(make_sales())
    assert len(customers) == 3                       # the row without an ID is dropped
    c1 = customers[customers["customer_id"] == 1].iloc[0]
    assert c1["frequency"] == 2                      # two different invoices
    assert c1["monetary"] == pytest.approx(40.0)
    # Median price of product A is 2.0. Customer 2 paid 1.0 -> 50% discount.
    c2 = customers[customers["customer_id"] == 2].iloc[0]
    assert c2["avg_discount_pct"] == pytest.approx(50.0)


def test_segment_summary_revenue_shares_add_up_to_100():
    summary = summarize_segments(calculate_rfm(make_sales()))
    assert summary["revenue_share_pct"].sum() == pytest.approx(100.0)
