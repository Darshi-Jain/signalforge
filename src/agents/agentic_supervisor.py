from __future__ import annotations

from agents import Agent, ModelSettings, Runner

from src.agents.specialist_tools import (
    investigate_commercial_risk,
    investigate_product_adoption,
    investigate_relationship_risk,
    investigate_support_risk,
    investigate_voice_of_customer,
)
from src.models.agentic_investigation import AgenticInvestigation
from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.tools.agent_tools import customer_profile


SUPERVISOR_INSTRUCTIONS = """
You are the Customer Risk Investigation Supervisor for SignalForge.

Your job is to conduct an evidence-based investigation of a B2B SaaS
customer and decide whether the account is at meaningful churn or
retention risk.

You control several specialist investigation tools.

Available specialist domains:
- Product Adoption
- Support / Technical Risk
- Relationship / Stakeholder Risk
- Commercial / Renewal Risk
- Voice of Customer

You also have access to the customer profile.

Investigation strategy:

1. Start by retrieving basic customer context.
2. Decide which specialist investigations are relevant.
3. You do NOT have to call every specialist.
4. Use additional specialists when evidence from one domain suggests
   another domain may materially change the conclusion.
5. Compare findings across domains.
6. Look for confirming and contradictory evidence.
7. Stop once enough evidence exists for a defensible account-level
   conclusion.

Rules:

- Never invent customer facts.
- Do not simply average specialist risk scores.
- Overall risk should reflect severity, evidence quality, agreement
  between independent domains, ARR/renewal context when available,
  and contradictory positive signals.
- One severe specialist finding may justify escalation, but explain why.
- Distinguish churn risk from operational inconvenience.
- Clearly identify missing information.
- Recommended actions must directly address identified evidence.
- Include only specialists actually consulted in specialists_consulted.
"""


def build_supervisor_agent() -> Agent:
    return Agent(
        name="SignalForge Customer Risk Supervisor",
        instructions=SUPERVISOR_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            customer_profile,
            investigate_product_adoption,
            investigate_support_risk,
            investigate_relationship_risk,
            investigate_commercial_risk,
            investigate_voice_of_customer,
        ],
        output_type=AgenticInvestigation,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_customer_agentically(
    customer_id: str,
):
    result = await Runner.run(
        build_supervisor_agent(),
        input=(
            "Conduct a complete customer-risk investigation for "
            f"{customer_id}. Decide which specialists are necessary "
            "and return an evidence-backed account assessment."
        ),
        max_turns=12,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
