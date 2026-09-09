"""Sample Nigerian household data for demos and tests."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from naira_pulse.models import Bill, CashBuffer, FxQuote
from naira_pulse.store import reset_store, save_bills, save_buffer, save_fx


def _due(days_from_today: int, *, as_of: date | None = None) -> str:
    base = as_of or date.today()
    return (base + timedelta(days=days_from_today)).isoformat()


def sample_bills(*, as_of: date | None = None, paid_rent: bool = False) -> list[Bill]:
    """Canonical everyday bills: rent, DSTV, MTN, generator fuel."""
    today = as_of or date.today()
    return [
        Bill(
            id="rent001",
            name="Rent",
            amount_ngn=450_000,
            due_date=_due(7, as_of=today),
            category="housing",
            cadence="monthly",
            paid=paid_rent,
            notes="Lagos 2-bed — landlord prefers transfer before the 10th",
        ),
        Bill(
            id="dstv001",
            name="DSTV",
            amount_ngn=24_500,
            due_date=_due(3, as_of=today),
            category="entertainment",
            cadence="monthly",
            paid=False,
            notes="Compact Plus bouquet",
        ),
        Bill(
            id="mtn001",
            name="MTN Data",
            amount_ngn=8_000,
            due_date=_due(2, as_of=today),
            category="telecom",
            cadence="monthly",
            paid=False,
            notes="Family data share",
        ),
        Bill(
            id="fuel001",
            name="Generator Fuel",
            amount_ngn=35_000,
            due_date=_due(5, as_of=today),
            category="energy",
            cadence="weekly",
            paid=False,
            notes="Diesel top-up for NEPA gaps",
        ),
    ]


def seed_quiet_scenario(*, as_of: date | None = None) -> dict:
    """Enough NGN buffer → agent stays quiet."""
    reset_store()
    today = as_of or date.today()
    bills = sample_bills(as_of=today)
    save_bills(bills)
    # Cover all upcoming bills with comfortable headroom.
    total = sum(b.amount_ngn for b in bills if not b.paid)
    save_buffer(CashBuffer(balance_ngn=total + 50_000, label="primary"))
    save_fx(
        FxQuote(
            pair="USD/NGN",
            rate=1590.0,
            baseline_rate=1580.0,
            as_of=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            source="seeded",
        )
    )
    return {"scenario": "quiet", "bills": len(bills), "buffer_ngn": total + 50_000}


def seed_alert_scenario(*, as_of: date | None = None) -> dict:
    """Rent + utilities due, thin buffer → action alert."""
    reset_store()
    today = as_of or date.today()
    bills = sample_bills(as_of=today)
    save_bills(bills)
    # Only enough for DSTV + MTN — rent and fuel create a clear shortfall.
    save_buffer(CashBuffer(balance_ngn=40_000, label="primary"))
    save_fx(
        FxQuote(
            pair="USD/NGN",
            rate=1625.0,
            baseline_rate=1580.0,
            as_of=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            source="seeded",
        )
    )
    return {"scenario": "alert", "bills": len(bills), "buffer_ngn": 40_000}
