from __future__ import annotations

from agents import function_tool

from src.agents.agentic_adoption import investigate_adoption
from src.agents.agentic_commercial import investigate_commercial
from src.agents.agentic_relationship import investigate_relationship
from src.agents.agentic_support import investigate_support
from src.agents.agentic_voc import investigate_voc


@function_tool
async def investigate_product_adoption(customer_id: str) -> dict:
    """
    Ask the Product Adoption Specialist to investigate product usage risk.

    Use when usage decline, seat utilization, feature adoption, or
    product engagement may be relevant.
    """
    result = await investigate_adoption(customer_id)

    return result["finding"].model_dump()


@function_tool
async def investigate_support_risk(customer_id: str) -> dict:
    """
    Ask the Support Intelligence Specialist to investigate technical risk.

    Use when escalations, unresolved incidents, recurring issues, or
    customer support friction may be relevant.
    """
    result = await investigate_support(customer_id)

    return result["finding"].model_dump()


@function_tool
async def investigate_relationship_risk(customer_id: str) -> dict:
    """
    Ask the Relationship Intelligence Specialist to investigate
    stakeholder and engagement risk.

    Use when champion coverage, executive sponsorship, responsiveness,
    or stakeholder changes may be relevant.
    """
    result = await investigate_relationship(customer_id)

    return result["finding"].model_dump()


@function_tool
async def investigate_commercial_risk(customer_id: str) -> dict:
    """
    Ask the Commercial Risk Specialist to investigate contract,
    renewal, pricing, payment, or contraction risk.
    """
    result = await investigate_commercial(customer_id)

    return result["finding"].model_dump()


@function_tool
async def investigate_voice_of_customer(customer_id: str) -> dict:
    """
    Ask the Voice of Customer Specialist to investigate qualitative
    signals in customer conversations and meeting notes.
    """
    result = await investigate_voc(customer_id)

    return result["finding"].model_dump()
