"""Price elasticity per product and a rule-based price recommender.

Step 1 (estimate_elasticities): for each product, fit  log(units) = a + b * log(price) + c * log(store demand)
         -> b is the price elasticity: "+1% price changes units by b%".
Step 2 (recommend_prices): test prices around today's price, expect units = units_now * (price ratio)^b,
         and pick the price with the highest expected margin, inside the guardrails.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.kpis import COST_SHARE

# Which products can we estimate an elasticity for?
MIN_WEEKS = 30            # weeks with sales
MIN_PRICE_VARIATION = 0.05   # weekly price must vary by at least 5% (std / mean)
MIN_DISTINCT_PRICES = 4
BULK_LINE = 100           # order lines above this many units often have a bulk discount -> ignore for price

# "Current" state = the last 13 weeks (one quarter)
RECENT_WEEKS = 13
MIN_RECENT_WEEKS_SOLD = 6

# Default guardrails (the app lets you change them)
MAX_CHANGE = 0.10         # price may move at most +-10%
MIN_MARGIN = 0.25         # never cut the price below a 25% margin
ALPHA = 0.05              # elasticity must be significant at the 5% level
MIN_ELASTICITY = -5.0     # elasticities below this are not believable


# ---------- Step 1: elasticity ----------

def build_product_weeks(sales):
    """One row per product and week: units, list price and store-wide demand.

    List price = median line price of normal-sized order lines. We do NOT use
    revenue / units, because big orders get volume discounts, which would make
    "more units" and "lower average price" look related for the wrong reason.
    """
    normal_lines = sales[sales["quantity"] <= BULK_LINE]
    list_price = normal_lines.groupby(["stock_code", "week"])["price"].median().rename("list_price")

    units = sales.groupby(["stock_code", "week"])["quantity"].sum().rename("units")
    table = units.to_frame().join(list_price).dropna().reset_index()
    table["store_units"] = table.groupby("week")["units"].transform("sum")   # proxy for seasonality
    return table


def has_enough_price_variation(prices):
    variation = prices.std() / prices.mean()
    return variation >= MIN_PRICE_VARIATION and prices.round(2).nunique() >= MIN_DISTINCT_PRICES


def fit_elasticity(product_weeks):
    """Log-log regression for ONE product. Returns None if it cannot be fitted."""
    x = pd.DataFrame({
        "log_price": np.log(product_weeks["list_price"]),
        "log_store_units": np.log(product_weeks["store_units"]),
    })
    y = np.log(product_weeks["units"])
    try:
        result = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HC1")   # HC1 = robust standard errors
    except Exception:
        return None
    low, high = result.conf_int().loc["log_price"]
    return {
        "elasticity": result.params["log_price"],
        "p_value": result.pvalues["log_price"],
        "ci_low": low,
        "ci_high": high,
        "r_squared": result.rsquared,
    }


def estimate_elasticities(sales, descriptions):
    """Elasticity + current price/units/cost for every product with enough data."""
    weeks = build_product_weeks(sales)
    last_weeks = sorted(weeks["week"].unique())[-RECENT_WEEKS:]
    median_price = sales.groupby("stock_code")["price"].median()

    rows = []
    for code, part in weeks.groupby("stock_code"):
        if len(part) < MIN_WEEKS or not has_enough_price_variation(part["list_price"]):
            continue
        recent = part[part["week"].isin(last_weeks)]
        if len(recent) < MIN_RECENT_WEEKS_SOLD:
            continue                                    # not sold lately -> no price to recommend
        fit = fit_elasticity(part)
        if fit is None:
            continue
        rows.append({
            "stock_code": code,
            "description": descriptions.get(code, ""),
            "n_weeks": len(part),
            **fit,
            "current_price": recent["list_price"].median(),
            "current_units_week": recent["units"].sum() / RECENT_WEEKS,
            "unit_cost": median_price[code] * COST_SHARE,   # ASSUMPTION: 60% of median price
        })
    return pd.DataFrame(rows)


# ---------- Step 2: recommender ----------

def best_price(current_price, current_units, unit_cost, elasticity, max_change, min_margin):
    """Try prices from -max_change to +max_change in 1% steps; return the best price change."""
    best_change = 0.0
    best_margin = (current_price - unit_cost) * current_units       # margin if we change nothing

    for step in range(-round(max_change * 100), round(max_change * 100) + 1):
        change = step / 100
        price = current_price * (1 + change)
        margin_pct = (price - unit_cost) / price
        if change < 0 and margin_pct < min_margin:
            continue                                                  # guardrail: minimum margin
        units = current_units * (1 + change) ** elasticity            # the elasticity formula
        margin = (price - unit_cost) * units
        if margin > best_margin + 1e-9:
            best_margin, best_change = margin, change
    return best_change


def recommend_prices(elasticities, max_change=MAX_CHANGE, min_margin=MIN_MARGIN, alpha=ALPHA):
    """Add the recommended price and the expected effect per week to the elasticity table."""
    rows = []
    for row in elasticities.itertuples():
        # Guardrail: do not change anything when we cannot trust the elasticity
        if row.p_value >= alpha:
            change, reason = 0.0, "not_significant"
        elif not (MIN_ELASTICITY <= row.elasticity < 0):
            change, reason = 0.0, "elasticity_out_of_range"
        else:
            change = best_price(row.current_price, row.current_units_week, row.unit_cost,
                                row.elasticity, max_change, min_margin)
            if change == 0:
                reason = "no_better_price"
            elif abs(change) >= max_change - 1e-9:
                reason = "max_change"          # the guardrail limited the change
            else:
                reason = "ok"

        # Expected effect per week at the recommended price
        new_price = row.current_price * (1 + change)
        elasticity = row.elasticity if reason in ("ok", "max_change") else 0.0
        new_units = row.current_units_week * (1 + change) ** elasticity
        rows.append({
            "recommended_price": new_price,
            "price_change_pct": change * 100,
            "reason": reason,
            "units_change_pct": ((1 + change) ** elasticity - 1) * 100,
            "revenue_change": new_price * new_units - row.current_price * row.current_units_week,
            "margin_change": ((new_price - row.unit_cost) * new_units
                              - (row.current_price - row.unit_cost) * row.current_units_week),
        })
    result = pd.concat([elasticities.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    result["decision"] = np.where(result["price_change_pct"] > 0, "raise",
                          np.where(result["price_change_pct"] < 0, "lower", "keep"))
    return result.sort_values("margin_change", ascending=False).reset_index(drop=True)


def price_curve(row, max_change=MAX_CHANGE):
    """Expected weekly margin for every price in the test range (for the chart)."""
    changes = np.arange(-round(max_change * 100), round(max_change * 100) + 1) / 100
    prices = row.current_price * (1 + changes)
    units = row.current_units_week * (1 + changes) ** row.elasticity
    return pd.DataFrame({"price": prices, "units": units,
                         "margin": (prices - row.unit_cost) * units})
