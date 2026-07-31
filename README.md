# Agentic Customer Intelligence

A backend-first MVP for detecting early B2B SaaS churn signals. It investigates product adoption, support experience, stakeholder engagement, commercial risk, and customer sentiment; validates contradictory evidence; prioritizes risk; and proposes human-approved retention actions.

## Why this design

This project intentionally starts without a large frontend. The core portfolio value is evidence-grounded agent orchestration, structured outputs, deterministic business tools, validation, guardrails, and evaluation.

## Current capabilities

- Five specialist risk analyzers
- Evidence and confidence attached to every finding
- Composite churn probability and customer health score
- Seasonal false-positive validation
- Human-approval flag on every recommended action
- Portfolio prioritization by probability × ARR
- CLI commands and automated tests
- Runs without an API key

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Investigate one customer

```bash
python main.py investigate --customer CUST-001
```

## Scan upcoming renewals

```bash
python main.py scan-portfolio --renewal-window 120
```

## Example scenarios

- `CUST-001`: genuine multi-signal critical risk
- `CUST-004`: seasonal usage decline requiring validation
- `CUST-005`: healthy customer with several quickly resolved support tickets

## Next milestone

Add an OpenAI Agents SDK supervisor that uses the repository functions as tools, delegates qualitative investigation, returns the same typed report, and records traces and evaluation results. The deterministic engine will remain as the baseline and fallback.
