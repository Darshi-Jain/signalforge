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


class MCPSupportFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


INSTRUCTIONS = """
You are the Support Intelligence Specialist for SignalForge.

Investigate whether technical or support issues create meaningful
customer risk.

Use only the SignalForge MCP tools available to you.

Investigation approach:
1. Retrieve aggregated support context first.
2. If there are critical, unresolved, reopened, recurring, or unusual
   support issues, inspect ticket-level history.
3. Search meeting notes only when customer conversation context is
   necessary to understand technical impact.
4. Stop once additional tool calls would not materially change the
   conclusion.

Rules:
- Only evaluate SUPPORT / TECHNICAL risk.
- Never infer relationship, commercial, renewal, pricing, or product
  adoption risk.
- Never invent support tickets or customer statements.
- Distinguish resolved incidents from active problems.
- Consider severity, recurrence, unresolved state, and customer impact.
- Every material conclusion must be grounded in MCP tool output.
- Use lower confidence when evidence is incomplete.
"""


async def investigate_support_via_mcp(customer_id: str):
    support_filter = create_static_tool_filter(
        allowed_tool_names=[
            "get_support_context",
            "get_support_history",
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
        tool_filter=support_filter,
    ) as mcp_server:

        agent = Agent(
            name="MCP Support Intelligence Specialist",
            instructions=INSTRUCTIONS,
            model=get_agent_model(),
            mcp_servers=[mcp_server],
            output_type=MCPSupportFinding,
            model_settings=ModelSettings(
                temperature=0.1,
                include_usage=True,
            ),
        )

        result = await Runner.run(
            agent,
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
