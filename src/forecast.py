"""Weekly demand forecast for the top products.

Two methods are compared on the last 12 weeks (a "backtest"):
  1. Seasonal naive (baseline): next week = the same week one year ago.
  2. LightGBM: a small model that learns from last weeks' sales and the week of the year.
"""
import lightgbm as lgb
import numpy as np
import pandas as pd

from src.kpis import add_week

TOP_N = 10               # how many products to forecast
MIN_WEEKS_SOLD = 60      # only products that sold in at least this many weeks
MAX_LINE_SHARE = 0.20    # skip products where ONE order line is >20% of all units
BACKTEST_WEEKS = 12
HORIZON = 8              # weeks ahead
SEASON = 52              # weeks in a year


def pick_top_products(sales):
    """Top products by revenue that have a steady weekly series."""
    stats = sales.groupby("stock_code").agg(
        description=("description", "first"),
        revenue=("revenue", "sum"),
        units=("quantity", "sum"),
        weeks_sold=("week", "nunique"),
        biggest_line=("quantity", "max"),
    )
    stats["biggest_line_share"] = stats["biggest_line"] / stats["units"]
    steady = stats[(stats["weeks_sold"] >= MIN_WEEKS_SOLD)
                   & (stats["biggest_line_share"] <= MAX_LINE_SHARE)]
    return steady.sort_values("revenue", ascending=False).head(TOP_N)


def prepare_sales(sales):
    """Add the week column and drop the first and last week (they are partial weeks)."""
    sales = add_week(sales.copy())
    weeks = sorted(sales["week"].unique())
    return sales[(sales["week"] > weeks[0]) & (sales["week"] < weeks[-1])]


def weekly_units(sales, codes):
    """Table: one row per week, one column per product, values = units sold."""
    sales = sales[sales["stock_code"].isin(codes)]
    table = sales.pivot_table(index="week", columns="stock_code", values="quantity",
                              aggfunc="sum", fill_value=0)
    all_weeks = pd.date_range(table.index.min(), table.index.max(), freq="W-MON")
    return table.reindex(all_weeks, fill_value=0)[list(codes)]    # missing weeks = 0 units


# ---------- Method 1: seasonal naive ----------

def seasonal_naive(history, horizon):
    """Forecast = what was sold in the same week one year (52 weeks) earlier."""
    n = len(history)
    return np.array([history[n + k - SEASON] for k in range(horizon)], dtype=float)


# ---------- Method 2: LightGBM ----------
# "Direct" forecasting: every feature is something we know at the forecast START.
# The model is told how many weeks ahead (step) it predicts, so it never has to
# feed its own predictions back in (that makes errors pile up).

FEATURES = ["step", "last_week", "avg_4", "avg_8", "last_year", "last_year_avg3", "week_of_year"]


def make_features(history, step, target_week):
    """Features to predict the week that is `step` weeks after the end of `history`."""
    n = len(history)
    last_year = n + step - 1 - SEASON       # position of the same week one year earlier
    return {
        "step": step,
        "last_week": history[n - 1],
        "avg_4": np.mean(history[n - 4:]),
        "avg_8": np.mean(history[n - 8:]),
        "last_year": history[last_year],
        "last_year_avg3": np.mean(history[last_year - 1:last_year + 2]),   # smoother
        "week_of_year": target_week.isocalendar().week,
    }


def scale_of(series):
    """Each product is divided by its average, so big and small sellers look alike."""
    return max(series.mean(), 1)


def train_model(series_by_product, weeks, max_step):
    """Train ONE model on all products, using many past forecast start points."""
    rows, targets = [], []
    for code, series in series_by_product.items():
        scaled = (series / scale_of(series)).tolist()
        for n in range(SEASON + 2, len(scaled)):          # n = how many weeks we know
            for step in range(1, max_step + 1):
                if n + step - 1 >= len(scaled):
                    break                                 # that target week is not in the data
                rows.append(make_features(scaled[:n], step, weeks[n + step - 1]))
                targets.append(scaled[n + step - 1])

    model = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=8,
                              min_child_samples=20, verbose=-1)
    model.fit(pd.DataFrame(rows)[FEATURES], targets)
    return model


def lgbm_forecast(model, series, last_week, horizon):
    """Forecast `horizon` weeks after `last_week` (the last week we have data for)."""
    scale = scale_of(series)
    history = (series / scale).tolist()
    rows = [make_features(history, step, last_week + pd.Timedelta(weeks=step))
            for step in range(1, horizon + 1)]
    predictions = model.predict(pd.DataFrame(rows)[FEATURES])
    return np.maximum(predictions, 0) * scale          # units cannot be negative


# ---------- Backtest and final forecast ----------

def mape(actual, predicted):
    """Mean absolute percentage error, only over weeks with sales (a 0 would divide by 0)."""
    actual, predicted = np.asarray(actual, float), np.asarray(predicted, float)
    ok = actual > 0
    return np.mean(np.abs(actual[ok] - predicted[ok]) / actual[ok]) * 100


def run_backtest(units):
    """Pretend the last 12 weeks are unknown, forecast them, then compare with the truth."""
    cut = len(units) - BACKTEST_WEEKS
    train, test = units.iloc[:cut], units.iloc[cut:]
    model = train_model({c: train[c] for c in units}, list(units.index), BACKTEST_WEEKS)

    rows = []
    for code in units.columns:
        naive = seasonal_naive(train[code].tolist(), BACKTEST_WEEKS)
        lgbm = lgbm_forecast(model, train[code], train.index[-1], BACKTEST_WEEKS)
        for i, week in enumerate(test.index):
            rows.append({"stock_code": code, "week": week, "actual": test[code].iloc[i],
                         "naive": naive[i], "lgbm": lgbm[i]})
    return pd.DataFrame(rows)


def run_forecast(units):
    """Train on ALL weeks and forecast the next 8 weeks."""
    model = train_model({c: units[c] for c in units}, list(units.index), HORIZON)
    future_weeks = [units.index[-1] + pd.Timedelta(weeks=s) for s in range(1, HORIZON + 1)]

    rows = []
    for code in units.columns:
        naive = seasonal_naive(units[code].tolist(), HORIZON)
        lgbm = lgbm_forecast(model, units[code], units.index[-1], HORIZON)
        for i, week in enumerate(future_weeks):
            rows.append({"stock_code": code, "week": week, "naive": naive[i], "lgbm": lgbm[i]})
    return pd.DataFrame(rows)


def mape_table(backtest, descriptions):
    """Error per product: baseline vs. LightGBM (lower is better)."""
    rows = []
    for code, part in backtest.groupby("stock_code"):
        rows.append({"stock_code": code, "description": descriptions[code],
                     "mape_naive": mape(part["actual"], part["naive"]),
                     "mape_lgbm": mape(part["actual"], part["lgbm"])})
    return pd.DataFrame(rows)
