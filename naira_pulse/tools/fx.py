"""USD/NGN FX tools (seeded rates in demo mode)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from naira_pulse.models import FxQuote
from naira_pulse.store import load_fx, save_fx

try:
    from strands import tool
except ImportError:  # pragma: no cover

    def tool(fn=None, **_kwargs):  # type: ignore
        if fn is None:
            return lambda f: f
        return fn


# Seeded mid-market style rates for offline demo (not live market data).
_SEEDED_USD_NGN = 1625.0
_SEEDED_BASELINE = 1580.0


@tool
def get_fx_rate(
    pair: str = "USD/NGN",
    rate: float | None = None,
    baseline_rate: float | None = None,
) -> dict[str, Any]:
    """Get the USD/NGN FX rate (seeded in DEMO_MODE; optional override for scenarios).

    Args:
        pair: Currency pair, default USD/NGN.
        rate: Optional override rate to seed/update the store (demo scenarios).
        baseline_rate: Optional baseline used to measure % move for alerts.
    """
    pair = (pair or "USD/NGN").upper().replace(" ", "")
    if pair not in {"USD/NGN", "USDNGN", "NGN/USD"}:
        return {"ok": False, "error": f"Unsupported pair: {pair}. Use USD/NGN."}

    normalized = "USD/NGN"
    existing = load_fx()

    if rate is not None:
        quote = FxQuote(
            pair=normalized,
            rate=float(rate),
            as_of=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            source="seeded",
            baseline_rate=float(
                baseline_rate
                if baseline_rate is not None
                else (existing.baseline_rate if existing and existing.baseline_rate else _SEEDED_BASELINE)
            ),
        )
        save_fx(quote)
        return {"ok": True, "fx": quote.to_dict(), "move_pct": quote.move_pct_vs_baseline()}

    if existing is None:
        quote = FxQuote(
            pair=normalized,
            rate=_SEEDED_USD_NGN,
            as_of=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            source="seeded",
            baseline_rate=_SEEDED_BASELINE,
        )
        save_fx(quote)
    else:
        quote = existing

    return {"ok": True, "fx": quote.to_dict(), "move_pct": quote.move_pct_vs_baseline()}
