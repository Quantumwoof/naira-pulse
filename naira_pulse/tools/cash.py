"""Cash buffer tools."""

from __future__ import annotations

from datetime import date
from typing import Any

from naira_pulse.config import LOOKAHEAD_DAYS
from naira_pulse.logic.buffer import compute_shortfall
from naira_pulse.models import CashBuffer
from naira_pulse.store import load_bills, load_buffer, save_buffer

try:
    from strands import tool
except ImportError:  # pragma: no cover

    def tool(fn=None, **_kwargs):  # type: ignore
        if fn is None:
            return lambda f: f
        return fn


@tool
def check_cash_buffer(
    set_balance_ngn: float | None = None,
    lookahead_days: int = LOOKAHEAD_DAYS,
) -> dict[str, Any]:
    """Inspect (and optionally update) the NGN cash buffer vs upcoming bills.

    Args:
        set_balance_ngn: If provided, overwrite the stored NGN buffer balance.
        lookahead_days: How many days ahead to sum unpaid bills.
    """
    buffer = load_buffer()
    if set_balance_ngn is not None:
        buffer = CashBuffer(balance_ngn=float(set_balance_ngn))
        save_buffer(buffer)

    report = compute_shortfall(
        load_bills(),
        buffer,
        as_of=date.today(),
        lookahead_days=int(lookahead_days),
    )
    return {
        "buffer": buffer.to_dict(),
        "shortfall": report.to_dict(),
    }
