"""Shared pytest fixtures — isolated temp data dir, no LLM."""

from __future__ import annotations

import os
from datetime import date

import pytest


@pytest.fixture()
def frozen_today() -> date:
    return date(2026, 9, 9)


@pytest.fixture()
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("NAIRA_PULSE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DEMO_MODE", "1")
    # Reload config paths bound at import time.
    import naira_pulse.config as config
    import naira_pulse.store as store

    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "BILLS_FILE", tmp_path / "bills.json")
    monkeypatch.setattr(config, "BUFFER_FILE", tmp_path / "cash_buffer.json")
    monkeypatch.setattr(config, "FX_FILE", tmp_path / "fx.json")
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(store, "BILLS_FILE", tmp_path / "bills.json")
    monkeypatch.setattr(store, "BUFFER_FILE", tmp_path / "cash_buffer.json")
    monkeypatch.setattr(store, "FX_FILE", tmp_path / "fx.json")
    return tmp_path
