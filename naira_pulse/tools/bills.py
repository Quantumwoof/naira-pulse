"""Bill management tools."""

from __future__ import annotations

from typing import Any

from naira_pulse.models import Bill
from naira_pulse.store import load_bills, save_bills, upsert_bill

try:
    from strands import tool
except ImportError:  # pragma: no cover - demo/tests without strands installed yet
    def tool(fn=None, **_kwargs):  # type: ignore
        if fn is None:
            return lambda f: f
        return fn


@tool
def list_bills(include_paid: bool = False) -> dict[str, Any]:
    """List tracked recurring bills (rent, DSTV, airtime, fuel, etc.).

    Args:
        include_paid: When True, include bills already marked paid.
    """
    bills = load_bills()
    if not include_paid:
        bills = [b for b in bills if not b.paid]
    return {
        "count": len(bills),
        "bills": [b.to_dict() for b in bills],
    }


@tool
def add_bill(
    name: str,
    amount_ngn: float,
    due_date: str,
    category: str = "general",
    cadence: str = "monthly",
    notes: str = "",
) -> dict[str, Any]:
    """Add a new bill to the Naira Pulse tracker.

    Args:
        name: Human-readable bill name (e.g. Rent, DSTV).
        amount_ngn: Amount due in Nigerian Naira.
        due_date: Due date as YYYY-MM-DD.
        category: Category tag (housing, entertainment, telecom, energy, ...).
        cadence: monthly | weekly | one_off.
        notes: Optional free-text notes.
    """
    if amount_ngn <= 0:
        return {"ok": False, "error": "amount_ngn must be positive"}
    bill = Bill(
        name=name.strip(),
        amount_ngn=float(amount_ngn),
        due_date=due_date.strip(),
        category=category.strip() or "general",
        cadence=cadence.strip() or "monthly",
        notes=notes or "",
    )
    upsert_bill(bill)
    return {"ok": True, "bill": bill.to_dict()}


@tool
def mark_paid(bill_id: str = "", bill_name: str = "") -> dict[str, Any]:
    """Mark a bill as paid by id or exact name match.

    Args:
        bill_id: Bill id returned by list_bills / add_bill.
        bill_name: Exact bill name if id is unknown.
    """
    bills = load_bills()
    target = None
    if bill_id:
        target = next((b for b in bills if b.id == bill_id), None)
    elif bill_name:
        needle = bill_name.strip().lower()
        target = next((b for b in bills if b.name.lower() == needle), None)
    else:
        return {"ok": False, "error": "Provide bill_id or bill_name"}

    if target is None:
        return {"ok": False, "error": "Bill not found"}

    target.paid = True
    save_bills(bills)
    return {"ok": True, "bill": target.to_dict()}
