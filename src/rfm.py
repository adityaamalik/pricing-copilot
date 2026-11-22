"""RFM scoring: Recency, Frequency, Monetary.

Every customer gets a score from 1 (worst) to 5 (best) for each of the three,
and then a segment name such as "Champions" or "At risk".
"""
import numpy as np
import pandas as pd

SEGMENT_ORDER = ["Champions", "Loyal", "New", "At risk", "Hibernating"]


def make_score(values, higher_is_better=True):
    """Turn numbers into scores 1-5 (the top 20% get a 5, the next 20% a 4, ...).

    rank(pct=True) gives every customer a position between 0 and 1.
    Customers with the same value get the same position, so ties are fair.
    """
    position = values.rank(pct=True, ascending=higher_is_better)
    return np.ceil(position * 5).astype(int)


def name_segment(r, f):
    """Turn the R and F scores into a segment name (first matching rule wins)."""
    if r >= 4 and f >= 4:
        return "Champions"      # bought recently AND often
    if r >= 3 and f >= 3:
        return "Loyal"          # buy regularly
    if r >= 4 and f <= 2:
        return "New"            # bought recently, but only a few times so far
    if r <= 2 and f >= 3:
        return "At risk"        # used to buy often, but went quiet
    return "Hibernating"        # everyone else: quiet and not frequent


def calculate_rfm(sales):
    """One row per customer with R, F, M, scores, segment, price paid and discount."""
    sales = sales[sales["customer_id"].notna()].copy()     # we cannot score unknown customers

    # "Today" = the day after the last invoice in the data
    today = sales["invoice_date"].max().normalize() + pd.Timedelta(days=1)

    # What the same quantity would cost at the product's usual (median) price
    median_price = sales.groupby("stock_code")["price"].transform("median")
    sales["list_value"] = sales["quantity"] * median_price

    customers = sales.groupby("customer_id").agg(
        country=("country", "first"),
        last_purchase=("invoice_date", "max"),
        frequency=("invoice", "nunique"),        # number of orders
        monetary=("revenue", "sum"),             # total spent
        units=("quantity", "sum"),
        list_value=("list_value", "sum"),
    )
    customers["recency"] = (today - customers["last_purchase"]).dt.days

    customers["avg_price_paid"] = customers["monetary"] / customers["units"]
    # Discount = how far below the usual price the customer paid (negative = paid more)
    customers["avg_discount_pct"] = (1 - customers["monetary"] / customers["list_value"]) * 100

    customers["r_score"] = make_score(customers["recency"], higher_is_better=False)  # recent = good
    customers["f_score"] = make_score(customers["frequency"])
    customers["m_score"] = make_score(customers["monetary"])
    customers["segment"] = [name_segment(r, f) for r, f in
                            zip(customers["r_score"], customers["f_score"])]

    customers.index = customers.index.astype(int)
    return customers.reset_index()


def summarize_segments(customers):
    """One row per segment: size, revenue share, average price paid and discount."""
    grouped = customers.groupby("segment").agg(
        customers=("customer_id", "count"),
        revenue=("monetary", "sum"),
        units=("units", "sum"),
        list_value=("list_value", "sum"),
        avg_recency_days=("recency", "mean"),
        avg_orders=("frequency", "mean"),
    )
    grouped["revenue_share_pct"] = grouped["revenue"] / grouped["revenue"].sum() * 100
    grouped["avg_price_paid"] = grouped["revenue"] / grouped["units"]
    grouped["avg_discount_pct"] = (1 - grouped["revenue"] / grouped["list_value"]) * 100
    grouped = grouped.drop(columns=["units", "list_value"])
    return grouped.reindex(SEGMENT_ORDER).reset_index()
