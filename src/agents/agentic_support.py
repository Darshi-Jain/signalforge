from __future__ import annotations

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.tools.agent_tools import (
    search_customer_notes,
    support_history,
    support_summary,
)


class SupportFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


SUPPORT_INSTRUCTIONS = """
You are the Support Intelligence Specialist for SignalForge.

Your job is to investigate whether technical or support issues create
meaningful customer risk.

Use tools rather than assuming facts.

Investigation approach:
1. Retrieve the support summary.
2. If there are critical, reopened, unresolved, or unusually slow cases,
   inspect the underlying support history.
3. If additional customer context is needed, search meeting notes for
   relevant support or technical concerns.
4. Stop once you have enough evidence to make a supported conclusion.

Rules:
- Only evaluate SUPPORT / TECHNICAL risk.
- Do not infer product adoption, relationship, commercial, or pricing risk.
- Never invent ticket metrics or customer statements.
- Every material conclusion must be grounded in tool output.
- High severity alone is not enough; consider recurrence, resolution,
  open status, and customer impact.
- Use lower confidence when evidence is incomplete.
"""


def build_support_agent() -> Agent:
    return Agent(
        name="Support Intelligence Specialist",
        instructions=SUPPORT_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            support_summary,
            support_history,
            search_customer_notes,
        ],
        output_type=SupportFinding,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_support(customer_id: str):
    result = await Runner.run(
        build_support_agent(),
        input=(
            "Investigate technical and support risk for "
            f"customer {customer_id}."
        ),
        max_turns=8,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
