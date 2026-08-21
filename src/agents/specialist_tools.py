from __future__ import annotations

from agents import function_tool

from src.agents.mcp_adoption import investigate_adoption_via_mcp
from src.agents.mcp_commercial import investigate_commercial_via_mcp
from src.agents.mcp_relationship import investigate_relationship_via_mcp
from src.agents.mcp_support import investigate_support_via_mcp
from src.agents.mcp_voc import investigate_voc_via_mcp


@function_tool
async def investigate_product_adoption(customer_id: str) -> dict:
    """
    Ask the MCP-backed Product Adoption Specialist to investigate
    product usage and adoption risk.
    """
    result = await investigate_adoption_via_mcp(customer_id)
    return result["finding"].model_dump()


@function_tool
async def investigate_support_risk(customer_id: str) -> dict:
    """
    Ask the MCP-backed Support Intelligence Specialist to investigate
    technical and support risk.
    """
    result = await investigate_support_via_mcp(customer_id)
    return result["finding"].model_dump()


@function_tool
async def investigate_relationship_risk(customer_id: str) -> dict:
    """
    Ask the MCP-backed Relationship Intelligence Specialist to investigate
    stakeholder and engagement risk.
    """
    result = await investigate_relationship_via_mcp(customer_id)
    return result["finding"].model_dump()


@function_tool
async def investigate_commercial_risk(customer_id: str) -> dict:
    """
    Ask the MCP-backed Commercial Risk Specialist to investigate
    contract, renewal, pricing, payment, and contraction risk.
    """
    result = await investigate_commercial_via_mcp(customer_id)
    return result["finding"].model_dump()


@function_tool
async def investigate_voice_of_customer(customer_id: str) -> dict:
    """
    Ask the MCP-backed Voice of Customer Specialist to investigate
    qualitative customer-language signals.
    """
    result = await investigate_voc_via_mcp(customer_id)
    return result["finding"].model_dump()
