"""Weekly pricing KPIs, deviation flags and suggested actions."""
import numpy as np
import pandas as pd

COST_SHARE = 0.60   # ASSUMPTION: unit cost = 60% of the product's median price

# First match wins, so the order matters (Christmas before everything else)
PRODUCT_GROUPS = {
    "Christmas": ["CHRISTMAS", "XMAS", "SANTA", "ADVENT", "REINDEER", "SNOWMAN"],
    "Bags": ["BAG", "SHOPPER", "PURSE", "WALLET"],
    "Kitchen & Dining": ["MUG", "CUP", "TEA", "CAKE", "JAR", "BOWL", "PLATE",
                         "SPOON", "KITCHEN", "LUNCH", "BOTTLE", "APRON"],
    "Home Decor": ["FRAME", "CANDLE", "LANTERN", "HOLDER", "CUSHION", "SIGN",
                   "CLOCK", "DOORMAT", "LIGHT", "MIRROR", "VASE", "HEART"],
    "Stationery & Gifts": ["CARD", "WRAP", "NOTEBOOK", "PENCIL", "PAPER",
                           "STICKER", "RIBBON", "GIFT"],
    "Toys & Games": ["TOY", "GAME", "DOLL", "PUZZLE", "BLOCKS"],
}


def get_product_group(description):
    text = str(description).upper()
    for group, words in PRODUCT_GROUPS.items():
        for word in words:
            if word in text:
                return group
    return "Other"


def add_week(df):
    """Add a 'week' column = the Monday of the week of each invoice."""
    df["week"] = df["invoice_date"].dt.to_period("W").dt.start_time
    return df


def add_product_group(df):
    # Only ~5,000 different descriptions, so classify those and map back (fast)
    lookup = {d: get_product_group(d) for d in df["description"].dropna().unique()}
    df["product_group"] = df["description"].map(lookup).fillna("Other")
    return df


def build_weekly_table(sales, returns):
    """One row per week x country x product group, with additive columns only.

    Ratios (avg price, margin %, return rate) are NOT stored here, because
    you cannot add or average ratios when the user filters. We compute them
    later from the sums.
    """
    sales = sales.copy()
    sales["unit_cost"] = sales.groupby("stock_code")["price"].transform("median") * COST_SHARE
    sales["cost"] = sales["quantity"] * sales["unit_cost"]
    sales = add_week(add_product_group(sales))
    returns = add_week(add_product_group(returns.copy()))

    keys = ["week", "country", "product_group"]
    sales_weekly = sales.groupby(keys).agg(
        revenue=("revenue", "sum"), units=("quantity", "sum"), cost=("cost", "sum"))
    returns_weekly = returns.groupby(keys).agg(returns_revenue=("returns_revenue", "sum"))

    weekly = sales_weekly.join(returns_weekly, how="outer").fillna(0).reset_index()

    # The first and last week are partial weeks -> drop them
    weeks = sorted(weekly["week"].unique())
    weekly = weekly[(weekly["week"] > weeks[0]) & (weekly["week"] < weeks[-1])]
    return weekly.reset_index(drop=True)


def add_ratios(kpi):
    revenue = kpi["revenue"].where(kpi["revenue"] > 0)      # 0 -> NaN, avoids dividing by 0
    units = kpi["units"].where(kpi["units"] > 0)
    kpi["avg_price"] = kpi["revenue"] / units
    kpi["margin_pct"] = (kpi["revenue"] - kpi["cost"]) / revenue * 100
    kpi["return_rate"] = kpi["returns_revenue"] / revenue * 100
    return kpi


def get_kpis(weekly, country="All", group="All"):
    """Filter the weekly table, then return ONE row per week with all KPIs."""
    if country != "All":
        weekly = weekly[weekly["country"] == country]
    if group != "All":
        weekly = weekly[weekly["product_group"] == group]

    kpi = weekly.groupby("week")[["revenue", "units", "cost", "returns_revenue"]].sum()

    # Weeks without any sale are missing -> put them back as zeros
    all_weeks = pd.date_range(kpi.index.min(), kpi.index.max(), freq="W-MON")
    kpi = kpi.reindex(all_weeks, fill_value=0)
    kpi.index.name = "week"
    return add_ratios(kpi).reset_index()


# Action texts in both languages. {p} = price change, {u} = units change.
ACTIONS = {
    "en": {
        "price_up_units_down": "Price {p} but units {u}: review prices on the top items.",
        "discount_no_lift": "Price {p} but units only {u}: the discount is not lifting volume, review it.",
        "margin_low": "Margin below normal: check discounts and low-margin items.",
        "demand_strong": "Units {u} at a flat price: demand is strong, test a small price increase and check stock.",
        "demand_drop": "Units {u} without a price change: check promotions, stock-outs or seasonality.",
        "unusual": "Unusual week: check for one-off large orders or data problems.",
    },
    "de": {
        "price_up_units_down": "Preis {p}, aber Absatz {u}: Preise der Top-Artikel prüfen.",
        "discount_no_lift": "Preis {p}, Absatz nur {u}: Der Rabatt steigert die Menge nicht, bitte prüfen.",
        "margin_low": "Marge unter dem Normalwert: Rabatte und margenschwache Artikel prüfen.",
        "demand_strong": "Absatz {u} bei gleichem Preis: Die Nachfrage ist stark, kleine Preiserhöhung testen und Lagerbestand prüfen.",
        "demand_drop": "Absatz {u} ohne Preisänderung: Aktionen, Lieferengpässe oder Saisoneffekte prüfen.",
        "unusual": "Ungewöhnliche Woche: Einmalige Großaufträge oder Datenprobleme prüfen.",
    },
}


def suggest_action(price_change, units_change, metric, is_high, lang="en"):
    """Rule-based text. Changes are fractions vs. last week (0.10 = +10%)."""
    p = f"{price_change:+.0%}"
    u = f"{units_change:+.0%}"

    if price_change > 0.05 and units_change < -0.15:
        rule = "price_up_units_down"
    elif price_change < -0.05 and units_change < 0.05:
        rule = "discount_no_lift"
    elif metric == "margin_pct" and not is_high:
        rule = "margin_low"
    elif units_change > 0.30 and price_change <= 0.02:
        rule = "demand_strong"
    elif units_change < -0.30 and abs(price_change) <= 0.05:
        rule = "demand_drop"
    else:
        rule = "unusual"
    return ACTIONS[lang][rule].format(p=p, u=u)


def pct_change(series):
    """Change vs. last week; a jump from 0 gives inf, which we treat as unknown."""
    return series.pct_change().replace([np.inf, -np.inf], np.nan)


def find_flags(kpi, window=8, n_std=2.0, wow_limit=0.50, lang="en"):
    """Flag a week if a KPI is outside its rolling mean +/- n_std, or moved more than wow_limit."""
    metrics = ["revenue", "units", "avg_price", "margin_pct"]
    price_change = pct_change(kpi["avg_price"])
    units_change = pct_change(kpi["units"])

    rows = []
    for metric in metrics:
        s = kpi[metric]
        # shift(1): compare each week with the PREVIOUS weeks, not including itself
        mean = s.rolling(window).mean().shift(1)
        std = s.rolling(window).std().shift(1)
        change = pct_change(s)

        outside_band = (s - mean).abs() > n_std * std
        big_move = change.abs() > wow_limit
        # weeks with no sales at all (e.g. Christmas closure) are not "deviations"
        flagged = (outside_band | big_move) & (kpi["revenue"] > 0)

        for i in kpi.index[flagged]:
            rows.append({
                "week": kpi.loc[i, "week"],
                "metric": metric,
                "value": s[i],
                "expected": mean[i],
                "change_vs_last_week": change[i],
                "action": suggest_action(
                    price_change[i] if pd.notna(price_change[i]) else 0,
                    units_change[i] if pd.notna(units_change[i]) else 0,
                    metric, s[i] > mean[i], lang),
            })

    columns = ["week", "metric", "value", "expected", "change_vs_last_week", "action"]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows).sort_values("week", ascending=False).reset_index(drop=True)
