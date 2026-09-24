"""Offline demo — quiet run + alert run with sample Nigerian bills.

Usage:
    DEMO_MODE=1 python -m naira_pulse.demo

No AWS credentials or Bedrock access required.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date

# Ensure demo mode before importing config-dependent modules.
os.environ.setdefault("DEMO_MODE", "1")

from naira_pulse.seed import seed_alert_scenario, seed_quiet_scenario
from naira_pulse.tools.alerts import decide_alert
from naira_pulse.tools.bills import list_bills
from naira_pulse.tools.cash import check_cash_buffer
from naira_pulse.tools.fx import get_fx_rate


def _banner(title: str) -> None:
    line = "=" * 64
    print(f"\n{line}\n {title}\n{line}")


def _pretty(label: str, payload: dict) -> None:
    print(f"\n-- {label} --")
    print(json.dumps(payload, indent=2, default=str))


def run_scenario(name: str, seeder) -> dict:
    _banner(f"Naira Pulse · {name.upper()} RUN")
    seed_info = seeder(as_of=date.today())
    print(f"Seeded: {seed_info}")

    bills = list_bills(include_paid=False)
    buffer = check_cash_buffer()
    fx = get_fx_rate()
    decision = decide_alert()

    _pretty("Bills", bills)
    _pretty("Cash buffer", buffer)
    _pretty("FX", fx)
    _pretty("Alert decision", decision)

    level = decision.get("level", "?")
    should_ping = decision.get("should_ping")
    reason = decision.get("reason", "")
    print(f"\n>>> RESULT: level={level} should_ping={should_ping}")
    print(f">>> {reason}")
    return decision


def main() -> int:
    print("Naira Pulse demo (DEMO_MODE=1) — no AWS/Bedrock required")
    print("Sample bills: Rent, DSTV, MTN Data, Generator Fuel")

    quiet = run_scenario("quiet", seed_quiet_scenario)
    alert = run_scenario("alert", seed_alert_scenario)

    _banner("SUMMARY")
    print(f"Quiet run → should_ping={quiet.get('should_ping')} ({quiet.get('level')})")
    print(f"Alert run → should_ping={alert.get('should_ping')} ({alert.get('level')})")

    ok = (quiet.get("should_ping") is False) and (alert.get("should_ping") is True)
    if not ok:
        print("\nDemo expectations failed: quiet must be silent, alert must ping.", file=sys.stderr)
        return 1

    # Leave store in quiet scenario so a follow-up AgentCore/app.py invoke
    # is not stuck on the alert seed from the second run.
    seed_quiet_scenario(as_of=date.today())
    print("\nDemo OK — quiet stayed quiet; alert pinged for a decision.")
    print("(Store reset to quiet scenario for any follow-up local invokes.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
