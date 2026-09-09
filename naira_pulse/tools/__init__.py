"""Strands-compatible tools for Naira Pulse."""

from naira_pulse.tools.alerts import decide_alert
from naira_pulse.tools.bills import add_bill, list_bills, mark_paid
from naira_pulse.tools.cash import check_cash_buffer
from naira_pulse.tools.fx import get_fx_rate

ALL_TOOLS = [
    list_bills,
    add_bill,
    mark_paid,
    check_cash_buffer,
    get_fx_rate,
    decide_alert,
]

__all__ = [
    "list_bills",
    "add_bill",
    "mark_paid",
    "check_cash_buffer",
    "get_fx_rate",
    "decide_alert",
    "ALL_TOOLS",
]
