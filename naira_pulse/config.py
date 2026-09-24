"""Runtime configuration for Naira Pulse."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project roots
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
DATA_DIR = Path(os.environ.get("NAIRA_PULSE_DATA_DIR", PROJECT_ROOT / "data"))

# Demo mode is ON by default so judges can run without AWS/Bedrock.
DEMO_MODE = os.environ.get("DEMO_MODE", "1").strip().lower() in {"1", "true", "yes", "on"}

# Cash-buffer planning window (days ahead to consider unpaid bills).
LOOKAHEAD_DAYS = int(os.environ.get("NAIRA_PULSE_LOOKAHEAD_DAYS", "14"))

# Alert when shortfall exceeds this NGN amount (decision needed).
SHORTFALL_ALERT_THRESHOLD_NGN = float(
    os.environ.get("NAIRA_PULSE_SHORTFALL_THRESHOLD", "5000")
)

# Alert when USD/NGN moves more than this % vs last seeded baseline.
FX_MOVE_ALERT_PCT = float(os.environ.get("NAIRA_PULSE_FX_MOVE_PCT", "3.0"))

# Default store filenames
BILLS_FILE = DATA_DIR / "bills.json"
BUFFER_FILE = DATA_DIR / "cash_buffer.json"
FX_FILE = DATA_DIR / "fx.json"
