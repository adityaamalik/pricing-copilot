"""Turn raw transactions into clean product sales."""

# Stock codes that are not real products (postage, fees, manual adjustments...)
NON_PRODUCT_CODES = {
    "POST", "DOT", "M", "C2", "D", "S", "B", "CRUK", "PADS",
    "BANK CHARGES", "AMAZONFEE", "ADJUST", "ADJUST2", "TEST001", "TEST002",
}


def clean_sales(df):
    """Keep only real product sales: no cancellations, returns, zero prices or fees."""
    is_cancellation = df["invoice"].str.startswith("C")
    is_return = df["quantity"] <= 0
    is_zero_price = df["price"] <= 0
    is_fee = df["stock_code"].str.upper().isin(NON_PRODUCT_CODES)

    keep = ~is_cancellation & ~is_return & ~is_zero_price & ~is_fee
    df = df[keep].copy()

    df = df.drop_duplicates()                    # the dataset has some exact duplicate rows
    df["revenue"] = df["quantity"] * df["price"]
    return df.reset_index(drop=True)

def clean_returns(df):
    """Keep only real product returns (cancelled invoices), for the return rate KPI."""
    is_cancellation = df["invoice"].str.startswith("C")
    is_negative = df["quantity"] < 0
    is_priced = df["price"] > 0
    is_fee = df["stock_code"].str.upper().isin(NON_PRODUCT_CODES)

    df = df[is_cancellation & is_negative & is_priced & ~is_fee].copy()
    df["returns_revenue"] = -df["quantity"] * df["price"]   # make it a positive amount
    return df.reset_index(drop=True)
