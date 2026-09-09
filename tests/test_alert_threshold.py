"""Alert threshold decisions — pure logic, no LLM."""

from __future__ import annotations

from datetime import datetime, timezone

from naira_pulse.logic.decide import decide_alert_from_state
from naira_pulse.models import CashBuffer, FxQuote
from naira_pulse.seed import sample_bills


def _fx(rate: float, baseline: float = 1580.0) -> FxQuote:
    return FxQuote(
        pair="USD/NGN",
        rate=rate,
        baseline_rate=baseline,
        as_of=datetime(2026, 9, 9, tzinfo=timezone.utc).isoformat(),
        source="seeded",
    )


def test_quiet_when_buffer_healthy(frozen_today):
    bills = sample_bills(as_of=frozen_today)
    total = sum(b.amount_ngn for b in bills)
    decision = decide_alert_from_state(
        bills,
        CashBuffer(balance_ngn=total + 50_000),
        _fx(1590.0),  # ~0.6% move — below default 3%
        as_of=frozen_today,
        shortfall_threshold_ngn=5_000,
        fx_move_alert_pct=3.0,
    )
    assert decision.should_ping is False
    assert decision.level == "quiet"


def test_action_alert_on_shortfall_threshold(frozen_today):
    bills = sample_bills(as_of=frozen_today)
    decision = decide_alert_from_state(
        bills,
        CashBuffer(balance_ngn=40_000),
        _fx(1590.0),
        as_of=frozen_today,
        shortfall_threshold_ngn=5_000,
        fx_move_alert_pct=3.0,
    )
    assert decision.should_ping is True
    assert decision.level == "action"
    assert decision.shortfall_ngn >= 5_000
    assert "short" in decision.reason.lower() or "buffer" in decision.reason.lower()


def test_watch_alert_on_fx_move(frozen_today):
    # Only cheap bills within window relative to a fat buffer → no shortfall,
    # but FX spike should still ping.
    bills = sample_bills(as_of=frozen_today)
    total = sum(b.amount_ngn for b in bills)
    decision = decide_alert_from_state(
        bills,
        CashBuffer(balance_ngn=total + 100_000),
        _fx(1700.0, baseline=1580.0),  # ~7.6% move
        as_of=frozen_today,
        shortfall_threshold_ngn=5_000,
        fx_move_alert_pct=3.0,
    )
    assert decision.should_ping is True
    assert decision.level == "watch"
    assert decision.fx_move_pct is not None
    assert abs(decision.fx_move_pct) >= 3.0


def test_shortfall_below_threshold_stays_quiet_if_no_imminent_risk(frozen_today):
    # One small unpaid bill far enough (>3 days) with tiny shortfall under threshold.
    from naira_pulse.models import Bill

    bills = [
        Bill(
            id="small1",
            name="Newspaper",
            amount_ngn=3_000,
            due_date="2026-09-16",  # 7 days out from frozen_today
            category="other",
        )
    ]
    decision = decide_alert_from_state(
        bills,
        CashBuffer(balance_ngn=1_000),  # shortfall 2_000 < 5_000
        _fx(1585.0),
        as_of=frozen_today,
        shortfall_threshold_ngn=5_000,
        fx_move_alert_pct=3.0,
        lookahead_days=14,
    )
    assert decision.shortfall_ngn == 2_000
    assert decision.should_ping is False
    assert decision.level == "quiet"
