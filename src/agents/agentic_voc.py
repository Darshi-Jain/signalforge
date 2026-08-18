from __future__ import annotations

from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.tools.agent_tools import (
    meeting_notes,
    search_customer_notes,
)


class VoiceOfCustomerFinding(BaseModel):
    customer_id: str

    sentiment: str
    sentiment_score: float = Field(ge=-1, le=1)

    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

    competitor_mentioned: bool = False
    pricing_objection: bool = False
    product_gap_detected: bool = False
    churn_language_detected: bool = False
    expansion_signal_detected: bool = False

    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


VOC_INSTRUCTIONS = """
You are the Voice of Customer Intelligence Specialist for SignalForge.

Your job is to investigate qualitative signals contained in customer
conversations and meeting notes.

Use tools instead of assuming customer sentiment.

Investigation approach:

1. Retrieve recent customer meeting notes.
2. Analyze explicit customer language for:
   - positive or negative sentiment
   - competitor mentions
   - pricing objections
   - product gaps
   - churn or cancellation language
   - expansion or growth signals
3. If an important theme appears but needs more evidence, use
   search_customer_notes with a focused query.
4. Stop when enough qualitative evidence exists.

Rules:

- Only evaluate what is supported by customer conversation data.
- Never invent customer quotes or intentions.
- Do not infer a competitor mention unless a competitor or alternative
  is explicitly referenced.
- Do not classify general dissatisfaction as churn language unless
  cancellation, replacement, non-renewal, leaving, or equivalent
  intent is expressed.
- Do not treat a feature request alone as a severe product gap.
- Separate observations from interpretations.
- Every material conclusion must be grounded in retrieved notes.
- Organizational events such as champion departure may be reported as
  conversation context, but MUST NOT by themselves be treated as churn
  intent or severe Voice-of-Customer risk.
- Churn risk must be supported by explicit customer language such as
  cancellation, replacement, non-renewal, leaving, evaluating alternatives,
  or equivalent intent.
- Negative sentiment must reflect customer-expressed dissatisfaction,
  not merely an organizational event.
- If the notes contain factual organizational change but no customer
  dissatisfaction, use Neutral sentiment unless other language supports
  a different classification.
- Use lower confidence when few notes are available.
"""


def build_voc_agent() -> Agent:
    return Agent(
        name="Voice of Customer Intelligence Specialist",
        instructions=VOC_INSTRUCTIONS,
        model=get_agent_model(),
        tools=[
            meeting_notes,
            search_customer_notes,
        ],
        output_type=VoiceOfCustomerFinding,
        model_settings=ModelSettings(
            temperature=0.1,
            include_usage=True,
        ),
    )


async def investigate_voc(customer_id: str):
    result = await Runner.run(
        build_voc_agent(),
        input=(
            "Investigate Voice of Customer signals for "
            f"customer {customer_id}."
        ),
        max_turns=8,
    )

    return {
        "finding": result.final_output,
        "trace": extract_run_trace(result),
        "usage": result.context_wrapper.usage,
    }
