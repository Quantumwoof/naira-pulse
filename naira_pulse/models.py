"""Domain models for bills, cash buffer, FX, and alert decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Literal
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Bill:
    """A recurring or one-off bill denominated in NGN."""

    name: str
    amount_ngn: float
    due_date: str  # ISO date YYYY-MM-DD
    category: str = "general"
    cadence: str = "monthly"  # monthly | weekly | one_off
    paid: bool = False
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    notes: str = ""
    created_at: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Bill":
        return cls(
            id=str(raw.get("id") or str(uuid4())[:8]),
            name=str(raw["name"]),
            amount_ngn=float(raw["amount_ngn"]),
            due_date=str(raw["due_date"]),
            category=str(raw.get("category") or "general"),
            cadence=str(raw.get("cadence") or "monthly"),
            paid=bool(raw.get("paid", False)),
            notes=str(raw.get("notes") or ""),
            created_at=str(raw.get("created_at") or _utc_now_iso()),
        )

    def due_as_date(self) -> date:
        return date.fromisoformat(self.due_date[:10])


@dataclass
class CashBuffer:
    """NGN cash on hand that should cover upcoming bills."""

    balance_ngn: float
    currency: str = "NGN"
    label: str = "primary"
    updated_at: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CashBuffer":
        return cls(
            balance_ngn=float(raw.get("balance_ngn", 0)),
            currency=str(raw.get("currency") or "NGN"),
            label=str(raw.get("label") or "primary"),
            updated_at=str(raw.get("updated_at") or _utc_now_iso()),
        )


@dataclass
class FxQuote:
    """USD/NGN quote used for buffer decisions."""

    pair: str
    rate: float
    as_of: str
    source: str = "seeded"
    baseline_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "FxQuote":
        return cls(
            pair=str(raw.get("pair") or "USD/NGN"),
            rate=float(raw["rate"]),
            as_of=str(raw.get("as_of") or _utc_now_iso()),
            source=str(raw.get("source") or "seeded"),
            baseline_rate=(
                float(raw["baseline_rate"]) if raw.get("baseline_rate") is not None else None
            ),
        )

    def move_pct_vs_baseline(self) -> float | None:
        if self.baseline_rate is None or self.baseline_rate == 0:
            return None
        return ((self.rate - self.baseline_rate) / self.baseline_rate) * 100.0


AlertLevel = Literal["quiet", "watch", "action"]


@dataclass
class AlertDecision:
    """Whether Naira Pulse should ping a human."""

    level: AlertLevel
    should_ping: bool
    reason: str
    shortfall_ngn: float
    upcoming_bills_ngn: float
    buffer_ngn: float
    fx_move_pct: float | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
