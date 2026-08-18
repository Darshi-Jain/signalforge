from __future__ import annotations

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.tools.agent_tools import (
    compare_usage_with_segment,
    usage_trend,
)


class AdoptionFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

    summary: str

    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


ADOPTION_INSTRUCTIONS = """
You are the Product Adoption Specialist for SignalForge.

Your goal is to investigate whether a B2B SaaS customer has
meaningful product-adoption risk.

You have access to tools. Use them instead of assuming facts.

Investigation process:

1. Retrieve the customer's usage trend.
2. Evaluate active users, seat utilization, feature adoption,
   and other product-usage signals.
3. If usage appears weak or declining, compare the customer with
   similar customers in the same segment.
4. Gather enough evidence before making a conclusion.
5. Stop when additional tool calls would not materially change
   the conclusion.

Rules:

- Never invent metrics.
- Every important conclusion must be grounded in tool output.
- Only evaluate PRODUCT ADOPTION risk.
- Do not infer relationship, support, commercial, renewal, pricing,
  or churn risk.
- Do not use pre-existing risk labels as evidence.
- Distinguish customer-specific decline from broader segment behavior.
- Use low confidence when evidence is incomplete.
- Risk score must be between 0 and 100.
"""


def build_adoption_agent() -> Agent:
    return Agent(
        name="Product Adoption Specialist",
        instructions=ADOPTION_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            usage_trend,
            compare_usage_with_segment,
        ],
        output_type=AdoptionFinding,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_adoption(
    customer_id: str,
):
    from src.services.agent_trace import extract_run_trace

    agent = build_adoption_agent()

    result = await Runner.run(
        agent,
        input=(
            "Investigate product adoption risk for "
            f"customer {customer_id}."
        ),
        max_turns=8,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
