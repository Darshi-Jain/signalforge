# ⚡ SignalForge

## Agentic Customer Intelligence Platform

SignalForge is a multi-agent AI system built to help Customer Success and Account Management teams identify customer risk, understand why an account needs attention, and recommend evidence-backed next actions.

The system uses a Supervisor Agent that coordinates five specialist agents across Product Adoption, Support, Relationship Health, Commercial Risk, and Voice of Customer.

---

## What SignalForge Does

For each customer, SignalForge can analyze:

- Product usage and adoption
- Technical and support issues
- Champion and executive sponsor health
- Renewal and commercial risk
- Customer sentiment and meeting notes
- Positive and contradictory account signals

The final investigation produces:

- Overall risk
- Risk score
- Confidence
- Executive summary
- Risk drivers
- Evidence
- Positive signals
- Contradictory signals
- Missing information
- Recommended next actions
- Specialists consulted

---

## Architecture

```text
                    Streamlit UI
                         │
                         ▼
                  Supervisor Agent
                         │
               Profile + Risk Triage
                         │
              selects specialist agents
                         │
       ┌──────────┬──────────┬──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼          ▼
   Adoption    Support   Relationship Commercial    VoC
    Agent       Agent       Agent       Agent       Agent
       │          │          │          │          │
       └──────────┴──────────┼──────────┴──────────┘
                             │
                      MCP Tool Filters
                             │
                             ▼
                    SignalForge MCP Server
                             │
                 Services + Repositories
                             │
                             ▼
                        SQLite Data
```

---

## How the Architecture Works

SignalForge separates the application into distinct layers so that reasoning, data access, business logic, and presentation remain independent.

### 1. Streamlit UI

The Streamlit application is the user-facing layer.

It provides:

- Portfolio-level customer health monitoring
- Risk and renewal visibility
- Individual customer investigation
- AI-generated executive summaries
- Evidence-backed risk drivers
- Recommended next actions
- Agent execution and token-usage visibility

### 2. Supervisor Agent

The Supervisor is the orchestration layer of SignalForge.

Instead of sending all available customer data to one LLM, the Supervisor:

1. Retrieves basic customer context
2. Reviews risk-triage signals
3. Determines which specialist agents are relevant
4. Invokes those specialists
5. Compares evidence across domains
6. Identifies confirming and contradictory signals
7. Produces the final account-level assessment

The Supervisor does not simply average specialist scores. It considers the severity and quality of the evidence before reaching a conclusion.

---

## Specialist Agents

SignalForge currently includes five specialist agents.

### Product Adoption Agent

Investigates product engagement using signals such as:

- Active-user changes
- Seat utilization
- Feature adoption
- Usage trends
- Segment benchmarks

### Support Intelligence Agent

Investigates technical and support risk using:

- Critical tickets
- Unresolved tickets
- Recurring issues
- Ticket history
- Resolution patterns

### Relationship Intelligence Agent

Investigates stakeholder and engagement risk using:

- Active champions
- Executive sponsorship
- Stakeholder coverage
- Customer responsiveness
- CRM activity
- Champion departures

### Commercial Risk Agent

Investigates contractual and renewal risk using:

- Renewal timing
- Payment status
- Pricing objections
- Seat-reduction requests
- Budget and procurement signals

Commercial signals are interpreted in context. For example, a payment status of `Due Soon` is not automatically treated as payment risk without additional evidence.

### Voice of Customer Agent

Analyzes qualitative customer evidence from meeting notes for:

- Customer sentiment
- Competitor mentions
- Pricing objections
- Product gaps
- Explicit churn language
- Expansion signals

---

## Model Context Protocol (MCP)

SignalForge implements a Model Context Protocol server using the Python MCP SDK and FastMCP.

MCP provides a standardized interface between the AI agents and the underlying customer-data tools.

Examples of MCP tools include:

```text
get_customer_profile
get_usage_context
compare_usage_with_segment
get_support_context
get_support_history
get_relationship_context
get_commercial_context
get_recent_customer_notes
search_customer_notes
get_baseline_risk
```

### Why MCP?

In this portfolio implementation, customer information is stored locally.

In a production environment, customer intelligence could be distributed across systems such as:

```text
Salesforce
Gainsight
Zendesk
Snowflake
Jira
Product telemetry
Contract systems
Internal APIs
```

MCP creates a standardized boundary between the agents and these systems.

This means the reasoning layer does not need to be tightly coupled to a specific database or SaaS application.

### Least-Privilege Tool Access

Each specialist receives only the MCP tools necessary for its domain.

For example:

```text
Product Adoption Agent

Allowed:
✓ get_usage_context
✓ compare_usage_with_segment

Not exposed:
✗ get_support_history
✗ get_relationship_context
✗ get_commercial_context
```

This reduces unnecessary context, limits cross-domain contamination, and makes agent behavior easier to audit.

---

## AI Model

SignalForge currently uses:

**Gemini 2.5 Flash through Google Vertex AI**

The model is accessed through LiteLLM using a centralized model-provider abstraction.

```text
SignalForge Agent
       │
       ▼
get_agent_model()
       │
       ▼
    LiteLLM
       │
       ▼
 Google Vertex AI
       │
       ▼
Gemini 2.5 Flash
```

### Why Gemini 2.5 Flash?

Gemini 2.5 Flash was selected for the current implementation because it provides a practical balance of:

- Tool-calling capability
- Structured output generation
- Reasoning quality
- Low latency
- Cost efficiency
- Google Cloud integration

Analytical agents use low temperature settings to improve consistency.

The model-provider layer is kept separate from the individual agents so that other models can be evaluated later without redesigning the agent architecture.

---

## Evidence Grounding

SignalForge does not rely solely on an LLM's interpretation.

The system combines agent reasoning with deterministic grounding checks.

For Voice of Customer analysis, SignalForge validates that:

- Referenced evidence exists
- Evidence maps back to actual customer notes
- Competitor claims are supported
- Churn claims are explicitly supported
- Organizational changes are not automatically classified as negative customer sentiment

The flow is:

```text
Customer Evidence
       │
       ▼
    MCP Tool
       │
       ▼
 LLM Specialist
       │
       ▼
Structured Finding
       │
       ▼
Grounding Validation
       │
       ▼
Validated Finding
```

This helps reduce unsupported conclusions and improves the auditability of the system.

---

## Risk Triage

Before launching deeper specialist investigations, the Supervisor can use lightweight cross-domain signals to determine where investigation is most valuable.

Signals can include:

- Usage decline
- Seat utilization
- Critical support tickets
- Unresolved support issues
- Champion coverage
- Executive sponsorship
- Customer responsiveness
- Renewal timing
- Pricing objections

Risk triage is used for **routing**, not as the final customer-risk decision.

The final assessment is produced after the Supervisor evaluates specialist evidence.

---

## Evaluation Framework

SignalForge includes an evaluation framework for testing the behavior of the multi-agent system.

Representative evaluation scenarios include:

| Scenario | Expected Primary Specialist |
| --- | --- |
| Healthy Customer | Minimal investigation |
| Usage Decline | Product Adoption |
| Support Escalation | Support |
| Champion Departure | Relationship |
| Commercial Risk | Commercial |
| Competitor Risk | Voice of Customer |
| Seasonal Decline | Product Adoption |

The current representative Supervisor evaluation suite passes:

**7 / 7 scenarios**

The evaluation framework checks:

- Overall risk classification
- Required specialist selection
- Evidence presence
- Unsupported or forbidden claims
- Agent/tool execution
- LLM request count
- Input tokens
- Output tokens
- Total token usage

This provides a repeatable way to evaluate agent behavior instead of judging outputs only by whether they appear reasonable.

---

## Investigation Skills

SignalForge also supports reusable investigation playbooks.

Examples include:

- Churn Investigation
- Renewal Recovery
- Support Escalation
- Adoption Diagnosis

Skills provide procedural guidance to the agent while customer-specific facts must still come from retrieved evidence.

This separates **how an investigation should be performed** from **what is true about a particular customer**.

---

## Streamlit Application

SignalForge includes a Streamlit application with two main experiences.

### Portfolio View

The portfolio dashboard provides visibility into:

- Total customers
- High-risk accounts
- ARR at risk
- Upcoming renewals
- Customer segment
- Industry
- Risk level
- Risk score

### Investigation View

Users can select an individual customer and run the Agentic AI investigation.

The investigation UI presents:

- Overall risk
- Risk score
- Confidence
- Executive summary
- Risk drivers
- Supporting evidence
- Positive signals
- Contradictory signals
- Missing information
- Prioritized recommended actions
- Specialists consulted
- Agent/tool trace
- Token usage

---

## Technology Stack

### AI and Agentic Systems

- Gemini 2.5 Flash
- Google Vertex AI
- OpenAI Agents SDK runtime
- LiteLLM
- Model Context Protocol (MCP)
- FastMCP
- Pydantic structured outputs

### Backend

- Python
- SQLite
- Repository pattern
- Service layer

### Frontend

- Streamlit
- Pandas

### Cloud and Development

- Google Cloud
- Vertex AI
- Google Cloud Shell
- Git
- GitHub

### Testing and Evaluation

- Pytest
- Agent evaluation framework
- Tool-call tracing
- Token-usage tracking

---

## Project Structure

```text
signalforge/
│
├── app/
│   ├── streamlit_app.py
│   └── styles.css
│
├── evals/
│   ├── cases/
│   ├── results/
│   └── evaluate_supervisor.py
│
├── scripts/
│   ├── run_agentic_supervisor.py
│   ├── run_mcp_adoption.py
│   ├── run_mcp_support.py
│   ├── run_mcp_relationship.py
│   ├── run_mcp_commercial.py
│   ├── run_mcp_voc.py
│   └── test_mcp_server.py
│
├── skills/
│
├── src/
│   ├── agents/
│   ├── mcp/
│   ├── models/
│   ├── providers/
│   ├── repositories/
│   ├── services/
│   ├── tools/
│   └── workflows/
│
├── tests/
├── requirements.txt
└── README.md
```

---

## Running SignalForge

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Google Cloud

Authenticate using Google Cloud Application Default Credentials and configure the project used for Vertex AI.

```bash
gcloud auth application-default login
gcloud config set project signalforge-csm-ai
```

Set the required environment configuration:

```bash
export GOOGLE_CLOUD_PROJECT=signalforge-csm-ai
export GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. Test MCP

```bash
python scripts/test_mcp_server.py
```

### 5. Run an individual specialist

For example:

```bash
python scripts/run_mcp_support.py --customer CUST-0099
```

### 6. Run the Agentic Supervisor

```bash
python scripts/run_agentic_supervisor.py --customer CUST-0099
```

### 7. Run the evaluation suite

```bash
python evals/evaluate_supervisor.py
```

### 8. Launch the application

```bash
streamlit run app/streamlit_app.py
```

---

## Testing

Run the core test suite with:

```bash
python -m pytest -q
```

Current core test result:

```text
3 passed
```

Current representative Supervisor evaluation result:

```text
7 / 7 passed
```

---

## Current Status

Implemented:

- ✅ Synthetic customer intelligence dataset
- ✅ Deterministic customer-risk signals
- ✅ Five specialist AI agents
- ✅ Supervisor Agent orchestration
- ✅ Dynamic specialist selection
- ✅ Risk triage
- ✅ SignalForge MCP server
- ✅ MCP tool discovery and calling
- ✅ Least-privilege MCP tool access
- ✅ Structured agent outputs
- ✅ Voice of Customer evidence grounding
- ✅ Agent/tool execution tracing
- ✅ Token-usage tracking
- ✅ Investigation skills/playbooks
- ✅ Multi-agent evaluation framework
- ✅ 7/7 representative Supervisor evaluation scenarios
- ✅ Gemini 2.5 Flash through Vertex AI
- ✅ Streamlit portfolio dashboard
- ✅ Agentic investigation UI

---

## Future Work

Potential extensions include:

- Benchmarking additional models
- Self-hosted Hugging Face / vLLM model deployment on GCP
- Production MCP integrations with CRM and support systems
- Persistent investigation history
- Human approval workflows for high-impact actions
- Expanded evaluation datasets
- Latency and token-cost optimization
- Production authentication and authorization
- Cloud deployment of the application

---

## Key Engineering Idea

SignalForge is built around the idea that reliable agentic AI requires more than connecting an LLM to a collection of tools.

The architecture combines:

```text
LLM Reasoning
      +
Supervisor Orchestration
      +
Specialist Agents
      +
Least-Privilege MCP Tools
      +
Structured Outputs
      +
Evidence Grounding
      +
Execution Tracing
      +
Systematic Evaluation
```

This gives the system enough autonomy to investigate complex customer situations while keeping its conclusions grounded, observable, and testable.

---

## Author

**Darshi Jain**

Built as a portfolio project exploring agentic AI, Model Context Protocol, customer intelligence, evidence grounding, multi-agent orchestration, and AI evaluation.

