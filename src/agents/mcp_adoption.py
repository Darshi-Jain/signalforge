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


class MCPAdoptionFinding(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


INSTRUCTIONS = """
You are the Product Adoption Specialist for SignalForge.

Investigate product-adoption risk using only the SignalForge MCP
tools available to you.

Your scope is strictly:
- active-user change
- seat utilization
- feature adoption
- product engagement
- peer / segment usage comparison

Rules:
- Only evaluate product adoption.
- Never infer relationship, support, commercial, renewal, pricing,
  or churn risk.
- Never invent metrics.
- Every material conclusion must be grounded in MCP tool output.
- Compare the customer with peers when that materially changes
  interpretation.
- Use lower confidence when adoption evidence is incomplete.
"""


async def investigate_adoption_via_mcp(customer_id: str):
    adoption_filter = create_static_tool_filter(
        allowed_tool_names=[
            "get_usage_context",
            "compare_usage_with_segment",
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
        tool_filter=adoption_filter,
    ) as mcp_server:

        agent = Agent(
            name="MCP Product Adoption Specialist",
            instructions=INSTRUCTIONS,
            model=get_agent_model(),
            mcp_servers=[mcp_server],
            output_type=MCPAdoptionFinding,
            model_settings=ModelSettings(
                temperature=0.1,
                include_usage=True,
            ),
        )

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
