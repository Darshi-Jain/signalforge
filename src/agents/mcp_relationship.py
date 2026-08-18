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


class MCPRelationshipFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


INSTRUCTIONS = """
You are the Relationship Intelligence Specialist for SignalForge.

Your job is to determine whether stakeholder and relationship weakness
creates meaningful customer-retention risk.

Use only the SignalForge MCP tools available to you.

Investigation approach:
1. Retrieve structured relationship context first.
2. Evaluate:
   - active champion coverage
   - executive sponsorship
   - stakeholder depth
   - responsiveness
   - engagement recency
3. If structured signals indicate meaningful risk or ambiguity, search
   customer notes for focused relationship evidence.
4. Retrieve recent notes only if broader meeting context is necessary.
5. Stop once enough evidence exists.

Rules:
- Only evaluate RELATIONSHIP / STAKEHOLDER risk.
- Do not score adoption, support, commercial, pricing, or technical risk.
- Never invent stakeholder changes or customer statements.
- Distinguish an inactive individual from broader account weakness.
- Champion coverage and executive sponsorship are separate signals.
- No-response activity can indicate weak engagement but should be
  interpreted together with the broader relationship context.
- Every material conclusion must be grounded in MCP tool output.
- Reduce confidence when relationship evidence is incomplete.
"""


async def investigate_relationship_via_mcp(customer_id: str):
    relationship_filter = create_static_tool_filter(
        allowed_tool_names=[
            "get_relationship_context",
            "search_customer_notes",
            "get_recent_customer_notes",
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
        tool_filter=relationship_filter,
    ) as mcp_server:

        agent = Agent(
            name="MCP Relationship Intelligence Specialist",
            instructions=INSTRUCTIONS,
            model=get_agent_model(),
            mcp_servers=[mcp_server],
            output_type=MCPRelationshipFinding,
            model_settings=ModelSettings(
                temperature=0.1,
                include_usage=True,
            ),
        )

        result = await Runner.run(
            agent,
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
