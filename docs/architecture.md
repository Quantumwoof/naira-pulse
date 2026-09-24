# Naira Pulse Architecture

## Overview

Naira Pulse is a **background money agent** for everyday Nigerians. It watches recurring bills, the NGN cash buffer, and USD/NGN FX — and **only interrupts a human when a decision is needed**.

It is built for the **AWS Agents for Humans · Everyday Agents** hackathon using:

- **Strands Agents SDK** (`strands-agents`) for the agent + `@tool` loop
- **Amazon Bedrock AgentCore** (`BedrockAgentCoreApp` in `app.py`) for runtime hosting
- **Local JSON store** under `data/` for hackathon-friendly persistence (no bank API required)
- **DEMO_MODE=1** (default) so judges can run without AWS credentials

## Components

| Piece | Role |
| --- | --- |
| `app.py` | AgentCore entrypoint (`BedrockAgentCoreApp`) |
| `naira_pulse/agent.py` | Strands `Agent` factory + system prompt |
| `naira_pulse/tools/*` | `@tool` functions the agent can call |
| `naira_pulse/logic/*` | Pure Python shortfall + alert threshold (unit-tested) |
| `naira_pulse/store.py` | Thread-safe JSON read/write under `data/` |
| `naira_pulse/demo.py` | Offline quiet + alert scenarios |
| `tests/` | pytest for shortfall math and alert gates (no LLM) |

## Data flow

1. Bills, cash buffer, and FX quotes are loaded from `data/*.json`.
2. Tools expose CRUD / read APIs to the agent (`list_bills`, `add_bill`, `mark_paid`, `check_cash_buffer`, `get_fx_rate`, `decide_alert`).
3. `logic.buffer.compute_shortfall` sums unpaid bills inside a lookahead window and subtracts the NGN buffer.
4. `logic.decide.decide_alert_from_state` applies thresholds:
   - **action** if shortfall ≥ threshold
   - **watch** if FX move ≥ % threshold, or a bill is due ≤ 3 days with insufficient buffer
   - **quiet** otherwise
5. AgentCore `invoke` either runs the Strands agent (live Bedrock) or, in `DEMO_MODE`, returns a deterministic tool snapshot.

## Alert philosophy

Everyday agents fail when they nag. Naira Pulse is **quiet by default**. A ping means: *fund the buffer, defer a bill, or time a USD↔NGN move* — something only a human should decide.

## Deployment sketch

```
Local demo  →  python -m naira_pulse.demo
AgentCore   →  python app.py   # /invocations + /ping
Bedrock     →  Strands Agent model provider (when DEMO_MODE=0)
```

For production, swap the JSON store for DynamoDB / RDS and wire FX to a licensed market feed; keep the same tool contracts and alert thresholds.
