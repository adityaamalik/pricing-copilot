from types import SimpleNamespace

import pandas as pd
import pytest

from src.summary import (SYSTEM_PROMPT, build_summary_input, get_summary, make_prompt,
                         money, rule_based_summary)


def sample_data():
    return {
        "kpis": {"latest_week": "2011-11-28", "revenue_gbp": 1000, "revenue_change_vs_last_week_pct": 2.0,
                 "recent_flags": [{"week": "2011-11-07"}]},
        "customer_segments": [
            {"segment": "Champions", "customers": 10, "revenue_share_pct": 70.0},
            {"segment": "At risk", "customers": 5, "revenue_share_pct": 10.0}],
        "pricing_recommendations": {
            "products_analysed": 3, "recommended_raises": 2, "recommended_cuts": 1,
            "expected_margin_change_gbp_per_week": 120,
            "top_recommendations": [{"product": "MUG"}, {"product": "BAG"}]},
        "demand_forecast": {"avg_error_mape_pct_lightgbm": 55.6},
    }


class FakeClient:
    """Pretends to be the Anthropic client, so tests need no key and cost nothing."""
    def __init__(self):
        self.calls = 0
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **request):
        self.calls += 1
        reply = SimpleNamespace(type="text", text="## Key findings\n- fake answer")
        return SimpleNamespace(stop_reason="end_turn", content=[reply], model="fake-model")


def test_prompt_contains_data_and_language():
    system, user = make_prompt(sample_data(), "de")
    assert "German" in user and "Wichtigste Erkenntnisse" in user
    assert '"revenue_gbp": 1000' in user
    assert system == SYSTEM_PROMPT


def test_rule_based_summary_has_three_sections_in_both_languages():
    en = rule_based_summary(sample_data(), "en")
    de = rule_based_summary(sample_data(), "de")
    assert en.count("## ") == 3 and de.count("## ") == 3
    assert "+£120" in en and "+£120" in de


def test_money_format():
    assert money(3300) == "+£3,300" and money(-120) == "-£120"


def test_without_a_client_we_get_the_rule_based_text(tmp_path):
    result = get_summary(sample_data(), "en", client=None, cache_path=tmp_path / "cache.json")
    assert result["source"] == "rules"


def test_llm_answer_is_cached_and_reused(tmp_path):
    client, cache = FakeClient(), tmp_path / "cache.json"
    first = get_summary(sample_data(), "en", client=client, cache_path=cache)
    second = get_summary(sample_data(), "en", client=client, cache_path=cache)
    assert first["source"] == "llm" and second["source"] == "cache"
    assert second["text"] == first["text"]
    assert client.calls == 1                       # the second request did not call the API


def test_changed_data_does_not_reuse_the_old_answer(tmp_path):
    client, cache = FakeClient(), tmp_path / "cache.json"
    get_summary(sample_data(), "en", client=client, cache_path=cache)
    changed = sample_data()
    changed["kpis"]["revenue_gbp"] = 2000
    result = get_summary(changed, "en", client=client, cache_path=cache)
    assert result["source"] == "llm" and client.calls == 2


def test_refusal_falls_back_to_rule_based_text(tmp_path):
    client = FakeClient()
    client.create = lambda **r: SimpleNamespace(stop_reason="refusal", content=[], model="x")
    client.beta.messages.create = client.create
    result = get_summary(sample_data(), "en", client=client, cache_path=tmp_path / "c.json")
    assert result["source"] == "rules" and "declined" in result["error"]


def test_summary_input_is_built_from_the_real_tables():
    names = ["weekly_kpis", "rfm_customers", "elasticities", "forecast_errors", "forecast_future"]
    data = build_summary_input(*[pd.read_parquet(f"app_data/{n}.parquet") for n in names])
    assert set(data) == {"kpis", "customer_segments", "pricing_recommendations", "demand_forecast"}
    assert len(data["pricing_recommendations"]["top_recommendations"]) == 10
