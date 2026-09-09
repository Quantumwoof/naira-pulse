"""JSON file persistence for bills, cash buffer, and FX quotes."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from naira_pulse.config import BILLS_FILE, BUFFER_FILE, DATA_DIR, FX_FILE
from naira_pulse.models import Bill, CashBuffer, FxQuote

_lock = threading.RLock()


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def _read_json(path: Path, default: Any) -> Any:
    ensure_data_dir()
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, payload: Any) -> None:
    ensure_data_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def load_bills() -> list[Bill]:
    with _lock:
        raw = _read_json(BILLS_FILE, {"bills": []})
        items = raw.get("bills", raw if isinstance(raw, list) else [])
        return [Bill.from_dict(item) for item in items]


def save_bills(bills: list[Bill]) -> None:
    with _lock:
        _write_json(BILLS_FILE, {"bills": [b.to_dict() for b in bills]})


def upsert_bill(bill: Bill) -> Bill:
    with _lock:
        bills = load_bills()
        replaced = False
        for idx, existing in enumerate(bills):
            if existing.id == bill.id:
                bills[idx] = bill
                replaced = True
                break
        if not replaced:
            bills.append(bill)
        save_bills(bills)
        return bill


def load_buffer() -> CashBuffer:
    with _lock:
        raw = _read_json(BUFFER_FILE, None)
        if not raw:
            return CashBuffer(balance_ngn=0.0)
        return CashBuffer.from_dict(raw)


def save_buffer(buffer: CashBuffer) -> None:
    with _lock:
        _write_json(BUFFER_FILE, buffer.to_dict())


def load_fx() -> FxQuote | None:
    with _lock:
        raw = _read_json(FX_FILE, None)
        if not raw:
            return None
        return FxQuote.from_dict(raw)


def save_fx(quote: FxQuote) -> None:
    with _lock:
        _write_json(FX_FILE, quote.to_dict())


def reset_store() -> None:
    """Wipe demo store files (tests / demo reseeding)."""
    with _lock:
        ensure_data_dir()
        for path in (BILLS_FILE, BUFFER_FILE, FX_FILE):
            if path.exists():
                path.unlink()
