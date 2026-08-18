from __future__ import annotations

from agents import function_tool

from src.repositories import (
    ContractRepository,
    CustomerRepository,
    MeetingRepository,
    RelationshipRepository,
    SupportRepository,
    UsageRepository,
)
from src.tools.customer_intelligence import (
    get_contract_risk,
    get_customer_profile,
    get_support_summary,
    get_usage_trend,
)


@function_tool
def customer_profile(customer_id: str) -> dict:
    """
    Retrieve the basic profile for a customer account.

    Use this tool when you need account metadata such as segment,
    industry, ARR, account owner, and lifecycle stage.
    """
    return get_customer_profile(customer_id).model_dump()


@function_tool
def usage_trend(customer_id: str) -> dict:
    """
    Retrieve recent customer usage and product-adoption signals.

    Use this tool when investigating product adoption, usage decline,
    seat utilization, feature adoption, or API activity.
    """
    return get_usage_trend(customer_id).model_dump()


@function_tool
def support_summary(customer_id: str) -> dict:
    """
    Retrieve aggregated support risk signals for a customer.

    Returns ticket volume, critical tickets, reopened tickets,
    unresolved tickets, and average resolution time.
    """
    return get_support_summary(customer_id).model_dump()


@function_tool
def support_history(customer_id: str) -> list[dict]:
    """
    Retrieve individual support tickets for a customer.

    Use this when summary metrics are not enough and specific ticket
    evidence is required.
    """
    return SupportRepository().get_customer_tickets(customer_id)


@function_tool
def relationship_signals(customer_id: str) -> dict:
    """
    Retrieve stakeholder and relationship-health information.

    Use this to investigate champions, executive sponsorship,
    stakeholder coverage, customer responsiveness, and engagement.
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


@function_tool
def contract_details(customer_id: str) -> dict:
    """
    Retrieve commercial and renewal information for a customer.

    Use this tool for renewal timing, pricing objections, payment
    status, seat reductions, and ARR context.
    """
    return get_contract_risk(customer_id).model_dump()


@function_tool
def meeting_notes(
    customer_id: str,
    limit: int = 6,
) -> list[dict]:
    """
    Retrieve recent customer meeting notes.

    Use this when the investigation requires customer sentiment,
    objections, competitor mentions, business outcomes, or churn
    language.
    """
    notes = MeetingRepository().get_customer_notes(customer_id)
    return notes[:limit]


@function_tool
def search_customer_notes(
    customer_id: str,
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search a customer's meeting notes for a specific concept.

    Example queries include competitor, pricing, renewal, reporting,
    adoption, cancellation, or executive sponsor.
    """
    return MeetingRepository().search_notes(
        customer_id=customer_id,
        query=query,
        limit=limit,
    )


@function_tool
def compare_usage_with_segment(customer_id: str) -> dict:
    """
    Compare the customer's latest usage signals with customers in the
    same segment.

    Use this to determine whether a usage decline is customer-specific
    or common across similar accounts.
    """
    customer = CustomerRepository().get_by_id(customer_id)

    if customer is None:
        raise ValueError(f"Unknown customer: {customer_id}")

    target = get_usage_trend(customer_id)

    peers = CustomerRepository().list_customers(limit=500)
    peer_values = []

    for peer in peers:
        if (
            peer["customer_id"] != customer_id
            and peer["segment"] == customer["segment"]
        ):
            try:
                peer_usage = get_usage_trend(peer["customer_id"])
                peer_values.append(
                    peer_usage.latest_seat_utilization
                )
            except ValueError:
                continue

    if not peer_values:
        return {
            "customer_id": customer_id,
            "segment": customer["segment"],
            "customer_seat_utilization":
                target.latest_seat_utilization,
            "segment_average": None,
            "difference": None,
        }

    segment_average = sum(peer_values) / len(peer_values)

    return {
        "customer_id": customer_id,
        "segment": customer["segment"],
        "customer_seat_utilization":
            round(target.latest_seat_utilization, 4),
        "segment_average": round(segment_average, 4),
        "difference": round(
            target.latest_seat_utilization - segment_average,
            4,
        ),
    }
