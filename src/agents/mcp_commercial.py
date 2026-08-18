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


class MCPCommercialFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


INSTRUCTIONS = """
You are the Commercial Risk Specialist for SignalForge.

Your job is to determine whether renewal, pricing, payment,
contraction, or contractual signals create meaningful commercial risk.

Use only the SignalForge MCP tools available to you.

Investigation approach:
1. Retrieve commercial context first.
2. Evaluate:
   - renewal timing
   - payment status
   - pricing objection
   - requested seat reduction
   - renewal urgency
3. If risk is meaningful or unclear, search customer notes for
   renewal, pricing, procurement, contraction, or budget context.
4. Retrieve recent meeting notes only when broader commercial context
   is necessary.
5. Stop once enough evidence exists.

Rules:
- Only evaluate COMMERCIAL / RENEWAL risk.
- Do not score relationship, product adoption, support, or technical risk.
- A renewal date alone does not create high risk.
- 'Due Soon' is not a payment problem unless there is evidence of
  overdue payment, payment delay, dispute, or concern.
- Relationship events may be noted only if they directly affect a
  documented commercial decision.
- Never invent contract terms or customer statements.
- Every material conclusion must be grounded in MCP tool output.
"""


async def investigate_commercial_via_mcp(customer_id: str):
    commercial_filter = create_static_tool_filter(
        allowed_tool_names=[
            "get_commercial_context",
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
        tool_filter=commercial_filter,
    ) as mcp_server:

        agent = Agent(
            name="MCP Commercial Risk Specialist",
            instructions=INSTRUCTIONS,
            model=get_agent_model(),
            mcp_servers=[mcp_server],
            output_type=MCPCommercialFinding,
            model_settings=ModelSettings(
                temperature=0.1,
                include_usage=True,
            ),
        )

        result = await Runner.run(
            agent,
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
