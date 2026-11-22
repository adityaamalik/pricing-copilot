import numpy as np
import pandas as pd
import pytest

from src.forecast import (lgbm_forecast, mape, prepare_sales, seasonal_naive,
                          train_model, weekly_units)


def test_seasonal_naive_repeats_the_same_week_of_last_year():
    history = list(range(60))                 # 0, 1, 2, ... 59
    forecast = seasonal_naive(history, horizon=3)
    # next weeks are index 60, 61, 62 -> one year (52 weeks) earlier = 8, 9, 10
    assert forecast.tolist() == [8, 9, 10]


def test_mape_ignores_weeks_without_sales():
    actual = [100, 0, 200]
    predicted = [110, 50, 150]
    # only weeks 1 and 3 count: (10% + 25%) / 2 = 17.5%
    assert mape(actual, predicted) == pytest.approx(17.5)


def test_weekly_units_fills_missing_weeks_with_zero():
    sales = pd.DataFrame({
        "invoice_date": pd.to_datetime(["2011-01-03", "2011-01-10", "2011-01-24", "2011-01-31",
                                        "2011-02-07", "2011-02-14"]),
        "stock_code": ["A"] * 6,
        "quantity": [5, 6, 7, 8, 9, 10],
    })
    sales = prepare_sales(sales)              # drops the first and last (partial) week
    table = weekly_units(sales, ["A"])
    assert table.index.is_monotonic_increasing
    assert 0 in table["A"].tolist()           # the missing week (2011-01-17) became 0


def test_lgbm_forecast_has_right_length_and_is_never_negative():
    weeks = pd.date_range("2010-01-04", periods=110, freq="W-MON")
    season = 100 + 50 * np.sin(np.arange(110) * 2 * np.pi / 52)     # a made-up yearly wave
    series = pd.Series(season, index=weeks)
    model = train_model({"A": series, "B": series * 2}, list(weeks), max_step=8)
    forecast = lgbm_forecast(model, series, weeks[-1], horizon=8)
    assert len(forecast) == 8
    assert (forecast >= 0).all()
