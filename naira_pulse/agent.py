"""Strands agent factory for Naira Pulse."""

from __future__ import annotations

from typing import Any

from naira_pulse.config import DEMO_MODE
from naira_pulse.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are Naira Pulse, a quiet background money agent for people in Nigeria.

Your job:
- Track recurring bills (rent, DSTV, MTN, generator fuel, etc.).
- Watch the NGN cash buffer that should cover upcoming bills.
- Watch USD/NGN FX only insofar as it affects buffer decisions.
- Stay silent unless a human decision is needed.

Rules:
- Prefer tools over guessing. Use list_bills, check_cash_buffer, get_fx_rate, then decide_alert.
- Only recommend pinging the user when decide_alert says should_ping=true.
- Speak in clear, practical Nigerian English. Use ₦ for naira amounts.
- Never invent live bank balances or live FX — use the tools / seeded store.
- Be concise: state the decision, the shortfall or FX move, and 1–2 next actions.
"""


def build_agent() -> Any:
    """Build a Strands Agent with Naira Pulse tools.

    In DEMO_MODE callers should prefer `naira_pulse.demo` (no Bedrock).
    """
    from strands import Agent

    kwargs: dict[str, Any] = {
        "name": "naira-pulse",
        "system_prompt": SYSTEM_PROMPT,
        "tools": ALL_TOOLS,
    }
    # When not in demo mode, Strands will use the configured model provider
    # (typically Amazon Bedrock). DEMO_MODE demos never call this path.
    if DEMO_MODE:
        # Still construct the agent graph for AgentCore wiring / inspection,
        # but demos must not invoke the model.
        pass
    return Agent(**kwargs)


def run_agent_prompt(prompt: str) -> str:
    """Invoke the live Strands agent (requires AWS/Bedrock when DEMO_MODE=0)."""
    agent = build_agent()
    result = agent(prompt)
    # Strands AgentResult exposes .message; fall back to str().
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and "text" in first:
                return str(first["text"])
        return str(message)
    if message is not None:
        return str(message)
    return str(result)
