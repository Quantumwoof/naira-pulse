"""Shortfall math — pure logic, no LLM."""

from __future__ import annotations

from datetime import date

from naira_pulse.logic.buffer import compute_shortfall, upcoming_unpaid_bills
from naira_pulse.models import Bill, CashBuffer
from naira_pulse.seed import sample_bills


def test_upcoming_unpaid_within_lookahead(frozen_today):
    bills = sample_bills(as_of=frozen_today)
    upcoming = upcoming_unpaid_bills(bills, as_of=frozen_today, lookahead_days=14)
    names = [b.name for b in upcoming]
    assert names == ["MTN Data", "DSTV", "Generator Fuel", "Rent"]


def test_paid_bills_excluded_from_shortfall(frozen_today):
    bills = sample_bills(as_of=frozen_today, paid_rent=True)
    buffer = CashBuffer(balance_ngn=100_000)
    report = compute_shortfall(bills, buffer, as_of=frozen_today, lookahead_days=14)
    assert "Rent" not in report.bill_names
    assert report.upcoming_bills_ngn == 24_500 + 8_000 + 35_000
    assert report.shortfall_ngn == 0.0


def test_shortfall_when_buffer_thin(frozen_today):
    bills = sample_bills(as_of=frozen_today)
    buffer = CashBuffer(balance_ngn=40_000)
    report = compute_shortfall(bills, buffer, as_of=frozen_today, lookahead_days=14)
    expected_total = 450_000 + 24_500 + 8_000 + 35_000
    assert report.upcoming_bills_ngn == expected_total
    assert report.shortfall_ngn == expected_total - 40_000
    assert report.has_shortfall is True


def test_no_shortfall_when_buffer_covers(frozen_today):
    bills = sample_bills(as_of=frozen_today)
    total = sum(b.amount_ngn for b in bills)
    buffer = CashBuffer(balance_ngn=total + 1)
    report = compute_shortfall(bills, buffer, as_of=frozen_today, lookahead_days=14)
    assert report.shortfall_ngn == 0.0
    assert report.has_shortfall is False


def test_bills_outside_window_ignored(frozen_today):
    bills = [
        Bill(
            id="far1",
            name="Annual Insurance",
            amount_ngn=200_000,
            due_date=date(2026, 12, 1).isoformat(),
            category="insurance",
        )
    ]
    buffer = CashBuffer(balance_ngn=0)
    report = compute_shortfall(bills, buffer, as_of=frozen_today, lookahead_days=14)
    assert report.upcoming_bills_ngn == 0
    assert report.shortfall_ngn == 0
