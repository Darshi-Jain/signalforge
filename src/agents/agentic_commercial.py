from __future__ import annotations

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.tools.agent_tools import (
    contract_details,
    meeting_notes,
    search_customer_notes,
)


class CommercialFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


COMMERCIAL_INSTRUCTIONS = """
You are the Commercial Risk Specialist for SignalForge.

Your job is to determine whether renewal, pricing, payment, or
contractual signals create meaningful commercial risk.

Use tools instead of assuming facts.

Investigation approach:
1. Retrieve contract details first.
2. Evaluate renewal timing, payment status, pricing objections,
   and requested seat reductions.
3. If commercial risk is meaningful or ambiguous, inspect recent
   meeting notes or search notes for renewal, pricing, contraction,
   procurement, or budget context.
4. Stop once enough evidence exists to make a supported conclusion.

Rules:
- Only evaluate COMMERCIAL / RENEWAL risk.
- Do not score product adoption, support, or relationship risk.
- Never invent contract terms or customer statements.
- A near renewal date alone does not automatically imply high risk.
- Distinguish renewal urgency from actual negative commercial signals.
- Every material conclusion must be grounded in tool output.
- Commercial risk scores must be driven primarily by commercial evidence:
  renewal timing, payment problems, pricing objections, seat contraction,
  procurement blockers, budget constraints, or explicit renewal intent.
- Relationship events such as champion departure may be mentioned as
  context, but MUST NOT independently increase the commercial risk score.
- A payment status of 'Due Soon' is not a payment problem by itself.
  Only treat it as risk when there is evidence of overdue payment,
  payment delay, dispute, or customer concern.
- Do not speculate that relationship changes will cause budget,
  procurement, or contract problems without explicit evidence.
- Reduce confidence if the commercial context is incomplete.
"""


def build_commercial_agent() -> Agent:
    return Agent(
        name="Commercial Risk Specialist",
        instructions=COMMERCIAL_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            contract_details,
            meeting_notes,
            search_customer_notes,
        ],
        output_type=CommercialFinding,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_commercial(customer_id: str):
    result = await Runner.run(
        build_commercial_agent(),
        input=(
            "Investigate commercial and renewal risk for "
            f"customer {customer_id}."
        ),
        max_turns=8,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
