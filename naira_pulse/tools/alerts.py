"""Alert decision tool — the quiet-by-default gate."""

from __future__ import annotations

from datetime import date
from typing import Any

from naira_pulse.config import (
    FX_MOVE_ALERT_PCT,
    LOOKAHEAD_DAYS,
    SHORTFALL_ALERT_THRESHOLD_NGN,
)
from naira_pulse.logic.decide import decide_alert_from_state
from naira_pulse.store import load_bills, load_buffer, load_fx

try:
    from strands import tool
except ImportError:  # pragma: no cover

    def tool(fn=None, **_kwargs):  # type: ignore
        if fn is None:
            return lambda f: f
        return fn


@tool
def decide_alert(
    lookahead_days: int = LOOKAHEAD_DAYS,
    shortfall_threshold_ngn: float = SHORTFALL_ALERT_THRESHOLD_NGN,
    fx_move_alert_pct: float = FX_MOVE_ALERT_PCT,
) -> dict[str, Any]:
    """Decide whether to ping the human. Quiet unless a decision is needed.

    Args:
        lookahead_days: Planning window for unpaid bills.
        shortfall_threshold_ngn: Minimum NGN shortfall that triggers an action ping.
        fx_move_alert_pct: Absolute % USD/NGN move vs baseline that triggers a watch ping.
    """
    decision = decide_alert_from_state(
        load_bills(),
        load_buffer(),
        load_fx(),
        as_of=date.today(),
        lookahead_days=int(lookahead_days),
        shortfall_threshold_ngn=float(shortfall_threshold_ngn),
        fx_move_alert_pct=float(fx_move_alert_pct),
    )
    return decision.to_dict()
