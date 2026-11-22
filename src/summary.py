"""AI management summary.

1. build_summary_input(): collect the key numbers from all tabs into one small dict (JSON).
2. get_summary(): ask Claude to write the summary from ONLY that JSON.
   - the answer is cached on disk, so a demo never waits
   - without an API key we fall back to a simple rule-based text
"""
import hashlib
import json
import os
from pathlib import Path

import anthropic
import pandas as pd

from src.kpis import COST_SHARE, find_flags, get_kpis
from src.pricing import recommend_prices
from src.rfm import summarize_segments

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "app_data" / "summary_cache.json"

MODEL = "claude-opus-5-5"
USE_FALLBACK = True      # if Claude declines a request, let the API retry on a fallback model

LANGUAGES = {"en": "English", "de": "German"}
HEADINGS = {
    "en": "## Key findings / ## Recommended actions / ## Risks",
    "de": "## Wichtigste Erkenntnisse / ## Empfohlene Maßnahmen / ## Risiken",
}

# ---------- The prompt (shown to the user in the app) ----------

SYSTEM_PROMPT = (
    "You are a pricing analyst writing a short briefing for the management of an online retailer. "
    "You only use the data you are given. You never invent numbers, products or causes. "
    "You are honest about uncertainty and about the assumptions behind the numbers."
)

USER_TEMPLATE = """Write a one-page management summary in {language}.

Use exactly these three section headings (as markdown ## headings): {headings}
- Key findings: exactly 3 bullet points, each with at least one number from the data.
- Recommended actions: exactly 3 bullet points; the decisions management should take THIS WEEK.
- Risks: 2 or 3 bullet points.

Rules:
- Use ONLY the numbers in the DATA below. Money is in GBP. If something is not in the data, do not claim it.
- State the key assumptions: unit cost is assumed to be {cost_share} of the product's median price, and
  elasticities come from historical data (indicative, not causal).
- Be concrete (name products or segments) and keep it under 300 words.
- Write for a manager: short sentences, no jargon.

DATA (JSON):
{data_json}
"""


# ---------- Step 1: collect the numbers ----------

def to_json(data):
    """JSON text of a dict; numpy numbers and dates are converted."""
    return json.dumps(data, indent=2, ensure_ascii=False,
                      default=lambda o: o.item() if hasattr(o, "item") else str(o))


def build_summary_input(weekly, customers, elasticities, forecast_errors, forecast_future):
    """Key numbers from tab 1 (KPIs), tab 2 (segments), tab 3 (forecast) and tab 4 (pricing)."""
    # Tab 1: latest week and the most recent deviation flags (all countries, all products)
    kpi = get_kpis(weekly)
    latest, previous = kpi.iloc[-1], kpi.iloc[-2]
    flags = find_flags(kpi).head(8)
    kpi_data = {
        "latest_week": str(latest["week"].date()),
        "revenue_gbp": round(latest["revenue"]),
        "revenue_change_vs_last_week_pct": round((latest["revenue"] / previous["revenue"] - 1) * 100, 1),
        "units": round(latest["units"]),
        "avg_price_gbp": round(latest["avg_price"], 2),
        "margin_pct_assumed_cost": round(latest["margin_pct"], 1),
        "return_rate_pct": round(latest["return_rate"], 1),
        "recent_flags": [{"week": str(r.week.date()), "kpi": r.metric, "value": round(r.value, 2),
                          "expected": round(r.expected, 2), "suggested_action": r.action}
                         for r in flags.itertuples()],
    }

    # Tab 2: segments
    segments = summarize_segments(customers).round(1)
    segment_data = segments[["segment", "customers", "revenue_share_pct", "avg_recency_days",
                             "avg_discount_pct"]].to_dict("records")

    # Tab 4: top recommendations and totals
    recs = recommend_prices(elasticities)
    top = recs[recs["decision"] != "keep"].head(10)
    pricing_data = {
        "products_analysed": len(recs),
        "recommended_raises": int((recs["decision"] == "raise").sum()),
        "recommended_cuts": int((recs["decision"] == "lower").sum()),
        "expected_margin_change_gbp_per_week": round(recs["margin_change"].sum()),
        "expected_revenue_change_gbp_per_week": round(recs["revenue_change"].sum()),
        "top_recommendations": [{
            "product": r.description, "current_price": round(r.current_price, 2),
            "recommended_price": round(r.recommended_price, 2), "elasticity": round(r.elasticity, 2),
            "p_value": round(r.p_value, 4), "units_change_pct": round(r.units_change_pct, 1),
            "margin_change_gbp_per_week": round(r.margin_change, 1)} for r in top.itertuples()],
    }

    # Tab 3: forecast quality and the next 8 weeks
    forecast_data = {
        "avg_error_mape_pct_baseline": round(forecast_errors["mape_naive"].mean(), 1),
        "avg_error_mape_pct_lightgbm": round(forecast_errors["mape_lgbm"].mean(), 1),
        "next_8_weeks_units_top10_lightgbm": round(forecast_future["lgbm"].sum()),
        "next_8_weeks_units_top10_same_weeks_last_year": round(forecast_future["naive"].sum()),
    }

    return {"kpis": kpi_data, "customer_segments": segment_data,
            "pricing_recommendations": pricing_data, "demand_forecast": forecast_data}


def make_prompt(data, language):
    """The two texts we send to the model: (system prompt, user prompt)."""
    user = USER_TEMPLATE.format(language=LANGUAGES[language], headings=HEADINGS[language],
                                cost_share=f"{COST_SHARE:.0%}", data_json=to_json(data))
    return SYSTEM_PROMPT, user


# ---------- Step 2: ask Claude ----------

def make_client(api_key=None):
    """An Anthropic client, or None if there is no API key."""
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    return anthropic.Anthropic(api_key=api_key) if api_key else None


def call_llm(client, system_prompt, user_prompt):
    """One request to Claude. Returns (text, model name)."""
    request = dict(
        model=MODEL,
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        output_config={"effort": "medium"},
    )
    if USE_FALLBACK:
        response = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **request)
    else:
        response = client.messages.create(**request)

    if response.stop_reason == "refusal":
        raise RuntimeError("The model declined to answer this request.")
    text = "".join(block.text for block in response.content if block.type == "text")
    return text.strip(), response.model


# ---------- Cache ----------

def cache_key(language, system_prompt, user_prompt):
    """Same prompt + same data = same key. Change the data and the old answer is not reused."""
    raw = f"{MODEL}|{language}|{system_prompt}|{user_prompt}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_cache(path=CACHE_FILE):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else {}


def save_cache(cache, path=CACHE_FILE):
    Path(path).write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def get_summary(data, language, client=None, cache_path=CACHE_FILE, refresh=False):
    """Return {"text", "source", "model", "error"}. source is "cache", "llm" or "rules"."""
    system_prompt, user_prompt = make_prompt(data, language)
    key = cache_key(language, system_prompt, user_prompt)
    cache = load_cache(cache_path)

    if key in cache and not refresh:
        return {**cache[key], "source": "cache", "error": None}

    error = None
    if client is not None:
        try:
            text, model = call_llm(client, system_prompt, user_prompt)
            cache[key] = {"text": text, "model": model}
            save_cache(cache, cache_path)
            return {"text": text, "source": "llm", "model": model, "error": None}
        except (anthropic.APIError, RuntimeError) as problem:
            error = str(problem)                 # fall through to the rule-based text

    return {"text": rule_based_summary(data, language), "source": "rules", "model": None, "error": error}


# ---------- Fallback without an LLM ----------

RULE_TEXT = {
    "en": {
        "h1": "## Key findings", "h2": "## Recommended actions", "h3": "## Risks",
        "f1": "In the latest week ({week}) revenue was £{revenue:,} ({change:+.1f}% vs. last week); the KPI monitor shows {n_flags} recent deviation flags.",
        "f2": "{segment} are {customer_share:.0f}% of customers but {revenue_share:.0f}% of revenue; {risk_customers:,} customers are in the 'At risk' segment.",
        "f3": "The pricing engine analysed {n} products: {raises} price raises and {cuts} price cuts would change weekly margin by about {margin}.",
        "a1": "Review the most recent KPI flags and check promotions, stock and large one-off orders behind them.",
        "a2": "Pilot the largest price changes on a few products first, for example: {products}. Compare with a control group.",
        "a3": "Run a win-back offer for the 'At risk' customers before they become inactive.",
        "r1": "Margin is based on an ASSUMED unit cost ({cost_share} of the median price), not on real costs.",
        "r2": "Elasticities come from historical data: indicative, not causal. Many products were tested, so some results are chance.",
        "r3": "Weekly forecasts are uncertain (average error {mape:.0f}% for the model); do not use single-product forecasts for firm decisions.",
        "note": "_Rule-based text: no LLM API key was available._",
    },
    "de": {
        "h1": "## Wichtigste Erkenntnisse", "h2": "## Empfohlene Maßnahmen", "h3": "## Risiken",
        "f1": "In der letzten Woche ({week}) lag der Umsatz bei £{revenue:,} ({change:+.1f}% zur Vorwoche); der KPI-Monitor zeigt {n_flags} aktuelle Abweichungs-Flags.",
        "f2": "{segment} sind {customer_share:.0f}% der Kunden, aber {revenue_share:.0f}% des Umsatzes; {risk_customers:,} Kunden sind im Segment 'At risk' (abwanderungsgefährdet).",
        "f3": "Die Preis-Engine hat {n} Produkte analysiert: {raises} Preiserhöhungen und {cuts} Preissenkungen würden die Wochenmarge um etwa {margin} verändern.",
        "a1": "Die jüngsten KPI-Flags prüfen und Aktionen, Lagerbestand und große Einmalbestellungen dahinter klären.",
        "a2": "Die größten Preisänderungen zuerst bei wenigen Produkten testen, zum Beispiel: {products}. Mit einer Kontrollgruppe vergleichen.",
        "a3": "Eine Rückgewinnungsaktion für die 'At risk'-Kunden starten, bevor sie inaktiv werden.",
        "r1": "Die Marge basiert auf ANGENOMMENEN Stückkosten ({cost_share} des Median-Preises), nicht auf echten Kosten.",
        "r2": "Die Elastizitäten stammen aus historischen Daten: indikativ, nicht kausal. Es wurden viele Produkte getestet, daher ist ein Teil der Ergebnisse Zufall.",
        "r3": "Wochenprognosen sind unsicher (durchschnittlicher Fehler {mape:.0f}% beim Modell); Einzelprodukt-Prognosen nicht für feste Entscheidungen nutzen.",
        "note": "_Regelbasierter Text: Es war kein LLM-API-Schlüssel verfügbar._",
    },
}


def money(amount):
    """+£3,300 or -£120"""
    return f"{'+' if amount >= 0 else '-'}£{abs(amount):,}"


def rule_based_summary(data, language):
    """A simple template summary built only from the numbers (no LLM)."""
    t = RULE_TEXT[language]
    kpis, pricing = data["kpis"], data["pricing_recommendations"]
    segments = pd.DataFrame(data["customer_segments"]).set_index("segment")
    best = segments["revenue_share_pct"].idxmax()
    customer_share = segments.loc[best, "customers"] / segments["customers"].sum() * 100
    products = ", ".join(r["product"] for r in pricing["top_recommendations"][:3])

    lines = [
        t["h1"],
        "- " + t["f1"].format(week=kpis["latest_week"], revenue=kpis["revenue_gbp"],
                              change=kpis["revenue_change_vs_last_week_pct"], n_flags=len(kpis["recent_flags"])),
        "- " + t["f2"].format(segment=best, customer_share=customer_share,
                              revenue_share=segments.loc[best, "revenue_share_pct"],
                              risk_customers=int(segments.loc["At risk", "customers"])),
        "- " + t["f3"].format(n=pricing["products_analysed"], raises=pricing["recommended_raises"],
                              cuts=pricing["recommended_cuts"],
                              margin=money(pricing["expected_margin_change_gbp_per_week"])),
        "", t["h2"], "- " + t["a1"], "- " + t["a2"].format(products=products), "- " + t["a3"],
        "", t["h3"],
        "- " + t["r1"].format(cost_share=f"{COST_SHARE:.0%}"), "- " + t["r2"],
        "- " + t["r3"].format(mape=data["demand_forecast"]["avg_error_mape_pct_lightgbm"]),
        "", t["note"],
    ]
    return "\n".join(lines)
