from __future__ import annotations

import sys

from agents import Agent, ModelSettings, Runner
from agents.mcp import (
    MCPServerStdio,
    create_static_tool_filter,
)
from pydantic import BaseModel, Field

from src.providers.agent_models import get_agent_model
from src.services.agent_trace import extract_run_trace
from src.services.voc_grounding import validate_voc_finding


class VoCEvidence(BaseModel):
    note_id: str
    evidence_text: str
    explanation: str


class MCPVoCFinding(BaseModel):
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
    evidence: list[VoCEvidence] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


INSTRUCTIONS = """
You are the Voice of Customer Intelligence Specialist for SignalForge.

Your job is to analyze ONLY what the customer communication says.

Use only the SignalForge MCP tools available to you.

Analyze for:
- customer sentiment
- competitor mentions
- pricing objections
- explicit product gaps
- churn / cancellation / non-renewal language
- expansion language

Important grounding rules:

1. Do not invent note IDs.
2. Every evidence item must use the exact note_id returned by a tool.
3. evidence_text must be copied from the retrieved note, not invented.
4. Champion departure or organizational change is NOT churn language.
5. Champion departure alone does NOT imply negative sentiment.
6. churn_language_detected may only be true when the customer note
   explicitly indicates leaving, cancellation, replacement,
   non-renewal, switching, or evaluating alternatives.
7. competitor_mentioned may only be true when an alternative provider
   or competitor is explicitly mentioned.
8. A feature request alone is not necessarily a product gap.
9. If notes contain only factual organizational changes, sentiment
   should normally be Neutral.
10. Never use knowledge outside retrieved customer notes.

Investigation approach:
1. Retrieve recent notes.
2. Analyze the literal customer language.
3. Search notes only when a focused theme requires more evidence.
4. Stop when sufficient evidence exists.
"""


async def investigate_voc_via_mcp(customer_id: str):
    voc_filter = create_static_tool_filter(
        allowed_tool_names=[
            "get_recent_customer_notes",
            "search_customer_notes",
        ]
    )

    async with MCPServerStdio(
        name="SignalForge MCP",
        params={
            "command": sys.executable,
            "args": [
                "-m",
                "src.mcp.server",
            ],
        },
        cache_tools_list=True,
        tool_filter=voc_filter,
    ) as mcp_server:

        agent = Agent(
            name="MCP Voice of Customer Specialist",
            instructions=INSTRUCTIONS,
            model=get_agent_model(),
            mcp_servers=[mcp_server],
            output_type=MCPVoCFinding,
            model_settings=ModelSettings(
                temperature=0.0,
                include_usage=True,
            ),
        )

        result = await Runner.run(
            agent,
            input=(
                "Analyze Voice of Customer evidence for "
                f"customer {customer_id}."
            ),
            max_turns=8,
        )

        validated = validate_voc_finding(
            customer_id=customer_id,
            finding=result.final_output,
        )

        return {
            "finding": validated,
            "trace": extract_run_trace(result),
            "usage": result.context_wrapper.usage,
        }
