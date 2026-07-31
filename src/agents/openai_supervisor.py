"""Optional LLM supervisor for the next milestone.

The deterministic investigation engine remains the source of numeric risk scores.
The agent explains evidence, challenges contradictions, and proposes actions.
"""
from __future__ import annotations
import json
from agents import Agent, Runner, function_tool
from src.tools.customer_tools import CustomerRepository
from src.orchestration.investigation import investigate
from src.models.schemas import InvestigationReport

repo = CustomerRepository()

@function_tool
def get_customer_account(customer_id: str) -> str:
    """Retrieve all structured signals for one customer account."""
    return json.dumps(repo.get_account(customer_id), default=str)

@function_tool
def run_baseline_investigation(customer_id: str) -> str:
    """Run the deterministic risk engine and return evidence-backed findings."""
    return investigate(repo.get_account(customer_id)).model_dump_json()

supervisor = Agent(
    name="Churn Investigation Supervisor",
    instructions=(
        "Investigate early churn risk for the requested B2B SaaS customer. "
        "Always call run_baseline_investigation. Treat its numeric calculations as authoritative. "
        "Use get_customer_account when more context is required. Do not invent facts. "
        "Preserve evidence, identify contradictions, and ensure all external actions require human approval."
    ),
    tools=[get_customer_account, run_baseline_investigation],
    output_type=InvestigationReport,
)

def run_agent_investigation(customer_id: str) -> InvestigationReport:
    result = Runner.run_sync(supervisor, f"Investigate customer {customer_id}.")
    return result.final_output
