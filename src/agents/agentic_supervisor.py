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
from src.tools.agent_tools import (
    customer_profile,
    risk_triage,
    load_investigation_skill,
)


SUPERVISOR_INSTRUCTIONS = """
You are the Customer Risk Investigation Supervisor for SignalForge.

Your job is to investigate B2B SaaS customer risk by deciding which
specialist agents are necessary, synthesizing their findings, and producing
an evidence-backed account-level assessment.

Available specialist investigations:
- Product Adoption
- Support / Technical Risk
- Relationship / Stakeholder Risk
- Commercial / Renewal Risk
- Voice of Customer

You also have access to basic customer profile context.

INVESTIGATION STRATEGY

1. Retrieve basic customer context first.
2. Decide which specialist investigations are materially relevant.
3. Do NOT automatically call every specialist.
4. Start with the domains most likely to explain the account's current risk.
5. Call another specialist only when:
   - the existing evidence suggests another domain may materially change
     the conclusion,
   - contradictory evidence requires validation,
   - or important account-level uncertainty remains.
6. Compare findings across independent domains.
7. Explicitly identify positive, negative, and contradictory signals.
8. Stop once additional specialist calls are unlikely to materially
   change the account-level conclusion.

REASONING RULES

- Never invent customer facts.
- Never treat a synthetic risk-profile label as evidence by itself.
- Do not simply average specialist risk scores.
- Give greater weight to:
  * severe evidence-grounded findings,
  * repeated evidence across independent domains,
  * unresolved critical issues,
  * explicit churn or commercial signals.
- Give balancing weight to strong positive or contradictory evidence.
- Operational problems do not automatically mean churn.
- Relationship risk does not automatically mean commercial risk.
- A lack of explicit churn language does not eliminate other material risks.
- Clearly report missing information.
- Recommended actions must directly address validated findings.
- specialists_consulted must contain only specialists actually invoked.
"""


def build_supervisor_agent() -> Agent:
    return Agent(
        name="SignalForge Customer Risk Supervisor",
        instructions=SUPERVISOR_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            customer_profile,
            risk_triage,
            load_investigation_skill,
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
            f"Investigate customer {customer_id}. "
            "Determine which specialist investigations are necessary. "
            "Use the minimum set of specialists required for a defensible "
            "customer-risk conclusion, escalating to additional specialists "
            "only when the evidence requires it."
        ),
        max_turns=12,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
