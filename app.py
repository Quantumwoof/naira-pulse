"""Amazon Bedrock AgentCore entrypoint for Naira Pulse.

Deploy with AgentCore Runtime (entrypoint: app.py). Local offline judges
should use `python -m naira_pulse.demo` instead (DEMO_MODE=1, no Bedrock).
"""

from __future__ import annotations

import os
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from naira_pulse.config import DEMO_MODE
from naira_pulse.tools import ALL_TOOLS

app = BedrockAgentCoreApp()

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from naira_pulse.agent import build_agent

        _agent = build_agent()
    return _agent


@app.entrypoint
def invoke(payload: dict[str, Any]):
    """AgentCore invocation handler.

    Expected payload: {"prompt": "..."}.
    When DEMO_MODE=1, returns a deterministic tool-based status instead of
    calling Bedrock — useful for local smoke tests of the entrypoint wiring.
    """
    prompt = payload.get("prompt") or payload.get("input", {}).get("prompt") or ""
    if not isinstance(prompt, str):
        prompt = str(prompt)

    if DEMO_MODE or os.environ.get("NAIRA_PULSE_FORCE_TOOLS") == "1":
        # Deterministic path — no LLM.
        from naira_pulse.tools.alerts import decide_alert
        from naira_pulse.tools.bills import list_bills
        from naira_pulse.tools.cash import check_cash_buffer
        from naira_pulse.tools.fx import get_fx_rate

        status = {
            "mode": "demo",
            "prompt": prompt,
            "bills": list_bills(),
            "cash_buffer": check_cash_buffer(),
            "fx": get_fx_rate(),
            "alert": decide_alert(),
            "tools": [getattr(t, "__name__", str(t)) for t in ALL_TOOLS],
        }
        return {"result": status}

    agent = _get_agent()
    result = agent(prompt or "Summarize my Naira Pulse status and whether I need a ping.")
    message = getattr(result, "message", str(result))
    return {"result": message}


if __name__ == "__main__":
    app.run()
