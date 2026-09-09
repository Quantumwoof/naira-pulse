"""Cash-buffer shortfall calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from naira_pulse.config import LOOKAHEAD_DAYS
from naira_pulse.models import Bill, CashBuffer


@dataclass(frozen=True)
class ShortfallReport:
    as_of: str
    lookahead_days: int
    buffer_ngn: float
    upcoming_bills_ngn: float
    shortfall_ngn: float
    bill_ids: tuple[str, ...]
    bill_names: tuple[str, ...]

    @property
    def has_shortfall(self) -> bool:
        return self.shortfall_ngn > 0

    def to_dict(self) -> dict:
        return {
            "as_of": self.as_of,
            "lookahead_days": self.lookahead_days,
            "buffer_ngn": self.buffer_ngn,
            "upcoming_bills_ngn": self.upcoming_bills_ngn,
            "shortfall_ngn": self.shortfall_ngn,
            "has_shortfall": self.has_shortfall,
            "bill_ids": list(self.bill_ids),
            "bill_names": list(self.bill_names),
        }


def upcoming_unpaid_bills(
    bills: list[Bill],
    *,
    as_of: date | None = None,
    lookahead_days: int = LOOKAHEAD_DAYS,
) -> list[Bill]:
    """Return unpaid bills due within the lookahead window (inclusive)."""
    today = as_of or date.today()
    horizon = today + timedelta(days=lookahead_days)
    selected: list[Bill] = []
    for bill in bills:
        if bill.paid:
            continue
        due = bill.due_as_date()
        if today <= due <= horizon:
            selected.append(bill)
    selected.sort(key=lambda b: (b.due_as_date(), b.name.lower()))
    return selected


def compute_shortfall(
    bills: list[Bill],
    buffer: CashBuffer,
    *,
    as_of: date | None = None,
    lookahead_days: int = LOOKAHEAD_DAYS,
) -> ShortfallReport:
    """Shortfall = max(0, upcoming unpaid bills − NGN cash buffer)."""
    today = as_of or date.today()
    upcoming = upcoming_unpaid_bills(
        bills, as_of=today, lookahead_days=lookahead_days
    )
    total = sum(b.amount_ngn for b in upcoming)
    shortfall = max(0.0, round(total - buffer.balance_ngn, 2))
    return ShortfallReport(
        as_of=today.isoformat(),
        lookahead_days=lookahead_days,
        buffer_ngn=float(buffer.balance_ngn),
        upcoming_bills_ngn=round(total, 2),
        shortfall_ngn=shortfall,
        bill_ids=tuple(b.id for b in upcoming),
        bill_names=tuple(b.name for b in upcoming),
    )
