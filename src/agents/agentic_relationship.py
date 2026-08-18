from __future__ import annotations

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.tools.agent_tools import (
    meeting_notes,
    relationship_signals,
    search_customer_notes,
)


class RelationshipFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


RELATIONSHIP_INSTRUCTIONS = """
You are the Relationship Intelligence Specialist for SignalForge.

Your job is to determine whether stakeholder and relationship weakness
creates meaningful customer-retention risk.

Use tools instead of assuming facts.

Investigation approach:
1. Retrieve relationship signals first.
2. Evaluate champion coverage, executive sponsorship, stakeholder depth,
   responsiveness, and engagement recency.
3. If the structured relationship data suggests meaningful risk or is
   ambiguous, inspect recent meeting notes or search notes for relationship
   context.
4. Stop once enough evidence exists to reach a supported conclusion.

Rules:
- Only evaluate RELATIONSHIP and STAKEHOLDER risk.
- Do not score product adoption, support, pricing, or commercial risk.
- Never invent stakeholder changes or customer statements.
- Distinguish a single inactive contact from broader relationship weakness.
- Consider executive sponsorship and champion strength separately.
- Every material conclusion must be grounded in tool output.
- Reduce confidence when stakeholder data is incomplete.
"""


def build_relationship_agent() -> Agent:
    return Agent(
        name="Relationship Intelligence Specialist",
        instructions=RELATIONSHIP_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            relationship_signals,
            meeting_notes,
            search_customer_notes,
        ],
        output_type=RelationshipFinding,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_relationship(customer_id: str):
    result = await Runner.run(
        build_relationship_agent(),
        input=(
            "Investigate stakeholder and relationship risk for "
            f"customer {customer_id}."
        ),
        max_turns=8,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
