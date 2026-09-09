"""Alert threshold logic — only ping when a human decision is needed."""

from __future__ import annotations

from datetime import date

from naira_pulse.config import (
    FX_MOVE_ALERT_PCT,
    LOOKAHEAD_DAYS,
    SHORTFALL_ALERT_THRESHOLD_NGN,
)
from naira_pulse.logic.buffer import ShortfallReport, compute_shortfall
from naira_pulse.models import AlertDecision, Bill, CashBuffer, FxQuote


def decide_alert_from_state(
    bills: list[Bill],
    buffer: CashBuffer,
    fx: FxQuote | None = None,
    *,
    as_of: date | None = None,
    lookahead_days: int = LOOKAHEAD_DAYS,
    shortfall_threshold_ngn: float = SHORTFALL_ALERT_THRESHOLD_NGN,
    fx_move_alert_pct: float = FX_MOVE_ALERT_PCT,
) -> AlertDecision:
    """
    Decide whether to interrupt the human.

    Rules (ordered):
    1. ACTION — shortfall >= threshold → ping (fund buffer / defer bill).
    2. WATCH — FX move vs baseline >= fx_move_alert_pct → ping (timing USD↔NGN).
    3. WATCH — any unpaid bill due within 3 days and buffer < that bill → ping.
    4. QUIET — otherwise stay silent.
    """
    today = as_of or date.today()
    report: ShortfallReport = compute_shortfall(
        bills, buffer, as_of=today, lookahead_days=lookahead_days
    )
    fx_move = fx.move_pct_vs_baseline() if fx else None

    details = {
        "report": report.to_dict(),
        "thresholds": {
            "shortfall_alert_ngn": shortfall_threshold_ngn,
            "fx_move_alert_pct": fx_move_alert_pct,
        },
    }

    if report.shortfall_ngn >= shortfall_threshold_ngn:
        return AlertDecision(
            level="action",
            should_ping=True,
            reason=(
                f"NGN cash buffer is short ₦{report.shortfall_ngn:,.0f} "
                f"for bills due in the next {lookahead_days} days "
                f"({', '.join(report.bill_names) or 'none'})."
            ),
            shortfall_ngn=report.shortfall_ngn,
            upcoming_bills_ngn=report.upcoming_bills_ngn,
            buffer_ngn=report.buffer_ngn,
            fx_move_pct=fx_move,
            details=details,
        )

    if fx_move is not None and abs(fx_move) >= fx_move_alert_pct:
        direction = "weaker" if fx_move > 0 else "stronger"
        return AlertDecision(
            level="watch",
            should_ping=True,
            reason=(
                f"USD/NGN moved {fx_move:+.1f}% ({direction} naira vs baseline). "
                "Decide whether to top up or hold your USD buffer."
            ),
            shortfall_ngn=report.shortfall_ngn,
            upcoming_bills_ngn=report.upcoming_bills_ngn,
            buffer_ngn=report.buffer_ngn,
            fx_move_pct=fx_move,
            details=details,
        )

    # Imminent single-bill risk even if aggregate shortfall is under threshold.
    for bill in bills:
        if bill.paid:
            continue
        days_until = (bill.due_as_date() - today).days
        if 0 <= days_until <= 3 and buffer.balance_ngn < bill.amount_ngn:
            return AlertDecision(
                level="watch",
                should_ping=True,
                reason=(
                    f"{bill.name} (₦{bill.amount_ngn:,.0f}) is due in {days_until} day(s) "
                    f"but buffer is only ₦{buffer.balance_ngn:,.0f}."
                ),
                shortfall_ngn=report.shortfall_ngn,
                upcoming_bills_ngn=report.upcoming_bills_ngn,
                buffer_ngn=report.buffer_ngn,
                fx_move_pct=fx_move,
                details=details,
            )

    return AlertDecision(
        level="quiet",
        should_ping=False,
        reason=(
            f"Quiet — buffer ₦{report.buffer_ngn:,.0f} covers "
            f"₦{report.upcoming_bills_ngn:,.0f} in upcoming bills."
        ),
        shortfall_ngn=report.shortfall_ngn,
        upcoming_bills_ngn=report.upcoming_bills_ngn,
        buffer_ngn=report.buffer_ngn,
        fx_move_pct=fx_move,
        details=details,
    )
