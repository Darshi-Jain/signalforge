from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.repositories import (
    CustomerRepository,
    MeetingRepository,
    RelationshipRepository,
    SupportRepository,
)
from src.services import calculate_customer_risk
from src.services.usage_benchmark import (
    compare_customer_usage_with_segment,
)
from src.tools import (
    get_contract_risk,
    get_recent_meeting_notes,
    get_support_summary,
    get_usage_trend,
)


mcp = FastMCP("SignalForge")


@mcp.tool()
def get_customer_profile(customer_id: str) -> dict:
    """
    Retrieve core account information for a SignalForge customer.

    Returns customer metadata such as name, industry, segment,
    ARR, owner, lifecycle stage, and synthetic risk profile.
    """
    customer = CustomerRepository().get_by_id(customer_id)

    if customer is None:
        raise ValueError(f"Unknown customer: {customer_id}")

    return customer


@mcp.tool()
def get_usage_context(customer_id: str) -> dict:
    """
    Retrieve current product usage and adoption signals.
    """
    return get_usage_trend(customer_id).model_dump()


@mcp.tool()
def get_support_context(customer_id: str) -> dict:
    """
    Retrieve aggregated customer support signals.
    """
    return get_support_summary(customer_id).model_dump()


@mcp.tool()
def get_commercial_context(customer_id: str) -> dict:
    """
    Retrieve contract, renewal, payment, pricing, and seat
    contraction information.
    """
    return get_contract_risk(customer_id).model_dump()


@mcp.tool()
def get_recent_customer_notes(
    customer_id: str,
    limit: int = 5,
) -> list[dict]:
    """
    Retrieve recent meeting notes for a customer.
    """
    notes = get_recent_meeting_notes(
        customer_id=customer_id,
        limit=limit,
    )

    return [
        note.model_dump()
        for note in notes
    ]


@mcp.tool()
def get_baseline_risk(customer_id: str) -> dict:
    """
    Retrieve SignalForge's deterministic baseline risk assessment.

    This is contextual evidence only. Agentic specialists should
    perform their own investigation rather than blindly accepting
    this score.
    """
    result = calculate_customer_risk(customer_id)

    return {
        "customer_id": customer_id,
        "risk_score": result["score"],
        "risk_level": result["level"],
        "weighted_average": result["weighted_average"],
        "strongest_signal": result["strongest_signal"],
    }


@mcp.tool()
def compare_usage_with_segment(customer_id: str) -> dict:
    """
    Compare customer seat utilization with similar customers
    in the same segment.
    """
    return compare_customer_usage_with_segment(customer_id)


@mcp.tool()
def get_support_history(customer_id: str) -> list[dict]:
    """
    Retrieve individual support tickets for a customer.

    Use this when aggregated support metrics are not enough and
    ticket-level evidence is required.
    """
    return SupportRepository().get_customer_tickets(customer_id)


@mcp.tool()
def get_relationship_context(customer_id: str) -> dict:
    """
    Retrieve customer stakeholder and engagement context.

    Includes champion coverage, executive sponsorship, stakeholder
    activity, and recent CRM engagement.
    """
    repo = RelationshipRepository()

    return {
        "summary": repo.get_summary(customer_id),
        "no_response_count": repo.get_no_response_count(customer_id),
        "stakeholders": repo.get_stakeholders(customer_id),
        "recent_crm_activity": repo.get_crm_activities(
            customer_id,
            limit=10,
        ),
    }


@mcp.tool()
def search_customer_notes(
    customer_id: str,
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search customer meeting notes for a focused concept such as
    support, renewal, pricing, champion, competitor, or product gap.
    """
    return MeetingRepository().search_notes(
        customer_id=customer_id,
        query=query,
        limit=limit,
    )


if __name__ == "__main__":
    mcp.run()
