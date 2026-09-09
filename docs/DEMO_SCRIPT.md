# Naira Pulse — Demo Script (≤ 5 minutes)

Target length: **4:00–4:45**. Speak to camera; show terminal + README architecture diagram.

## 0:00–0:30 — Hook

> “In Nigeria, rent, DSTV, MTN data, and generator fuel all hit at once — while the naira moves under you. Most finance apps spam you. **Naira Pulse only pings when you need to decide.**”

Show title slide / GitHub repo: `Quantumwoof/naira-pulse`.

## 0:30–1:15 — Problem & who

- **Who:** salaried / hustle households managing NGN cash + occasional USD.
- **Problem:** bill clustering + FX noise → either missed payments or notification fatigue.
- **Why an agent:** background watcher with tools beats another dashboard.

## 1:15–2:15 — Architecture (30–45s visual)

Open `README.md` Mermaid diagram or `docs/architecture.md`.

Call out:
1. Strands tools
2. JSON store
3. Pure alert logic (tested without LLM)
4. AgentCore `app.py` for AWS deploy

## 2:15–3:30 — Live demo (terminal)

```bash
cd naira-pulse
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DEMO_MODE=1 python -m naira_pulse.demo
```

Narrate two runs:

1. **Quiet run** — buffer covers Rent + DSTV + MTN + Generator Fuel → `should_ping=false`.
2. **Alert run** — thin ₦40k buffer vs ~₦517k bills → `level=action`, clear shortfall reason.

Optional one-liner:

```bash
pytest -q
```

Show green tests (shortfall + alert threshold, no Bedrock).

## 3:30–4:15 — Decision moment

Read the alert reason aloud. Emphasize: *the agent did not auto-pay — it asked a human to decide* (top up buffer, move USD, or defer).

Mention AgentCore path: `app.py` + `BedrockAgentCoreApp` for Everyday Agents on AWS.

## 4:15–4:45 — Close

> “Naira Pulse: everyday money calm. Quiet when you’re fine. Loud only when it matters.”

End on repo URL + `python -m naira_pulse.demo`.

## B-roll / cutaways (optional)

- Phone notification mock “Action needed: ₦ shortfall”
- Lagos apartment + generator (stock)
- USD/NGN chart flicking (seeded rate in demo)
