from __future__ import annotations

from src.models.tool_outputs import (
    ContractRisk,
    CustomerInvestigationContext,
    CustomerProfile,
    MeetingEvidence,
    SupportSummary,
    UsageTrend,
)
from src.repositories import (
    ContractRepository,
    CustomerRepository,
    MeetingRepository,
    SupportRepository,
    UsageRepository,
)


def get_customer_profile(customer_id: str) -> CustomerProfile:
    customer = CustomerRepository().get_by_id(customer_id)

    if customer is None:
        raise ValueError(f"Customer not found: {customer_id}")

    return CustomerProfile(
        customer_id=customer["customer_id"],
        customer_name=customer["customer_name"],
        industry=customer["industry"],
        segment=customer["segment"],
        arr=float(customer["arr"]),
        account_owner=customer["account_owner"],
        lifecycle_stage=customer["lifecycle_stage"],
        risk_profile=customer["risk_profile"],
    )


def get_usage_trend(customer_id: str) -> UsageTrend:
    monthly = UsageRepository().get_monthly_summary(customer_id)

    if not monthly:
        raise ValueError(f"No usage records found for: {customer_id}")

    latest = monthly[-1]
    previous = monthly[-2] if len(monthly) > 1 else latest

    latest_users = float(latest["active_users"])
    previous_users = float(previous["active_users"])

    if previous_users == 0:
        change_pct = 0.0
    else:
        change_pct = (
            (latest_users - previous_users) / previous_users
        ) * 100

    if change_pct <= -10:
        trend_direction = "declining"
    elif change_pct >= 10:
        trend_direction = "growing"
    else:
        trend_direction = "stable"

    return UsageTrend(
        customer_id=customer_id,
        months_available=len(monthly),
        latest_active_users=latest_users,
        previous_active_users=previous_users,
        active_user_change_pct=round(change_pct, 2),
        latest_seat_utilization=float(latest["seat_utilization"]),
        latest_feature_adoption=float(latest["feature_adoption_rate"]),
        latest_api_calls=int(latest["api_calls"]),
        trend_direction=trend_direction,
    )


def get_support_summary(customer_id: str) -> SupportSummary:
    summary = SupportRepository().get_summary(customer_id)

    if summary is None:
        raise ValueError(f"No support data found for: {customer_id}")

    return SupportSummary(
        customer_id=customer_id,
        total_tickets=int(summary["total_tickets"] or 0),
        critical_tickets=int(summary["critical_tickets"] or 0),
        reopened_tickets=int(summary["reopened_tickets"] or 0),
        unresolved_tickets=int(summary["unresolved_tickets"] or 0),
        average_resolution_hours=float(
            summary["average_resolution_hours"] or 0
        ),
    )


def get_contract_risk(customer_id: str) -> ContractRisk:
    contract = ContractRepository().get_by_customer(customer_id)
    customer = CustomerRepository().get_by_id(customer_id)

    if contract is None or customer is None:
        raise ValueError(f"Contract or customer not found: {customer_id}")

    renewal_days = int(contract["renewal_days"])

    if renewal_days <= 45:
        urgency = "critical"
    elif renewal_days <= 90:
        urgency = "high"
    elif renewal_days <= 180:
        urgency = "medium"
    else:
        urgency = "low"

    return ContractRisk(
        customer_id=customer_id,
        renewal_date=contract["renewal_date"],
        renewal_days=renewal_days,
        arr=float(customer["arr"]),
        payment_status=contract["payment_status"],
        requested_seat_reduction_pct=float(
            contract["requested_seat_reduction_pct"]
        ),
        pricing_objection=bool(contract["pricing_objection"]),
        urgency=urgency,
    )


def get_recent_meeting_notes(
    customer_id: str,
    limit: int = 5,
) -> list[MeetingEvidence]:
    notes = MeetingRepository().get_customer_notes(customer_id)

    return [
        MeetingEvidence(
            note_id=note["note_id"],
            meeting_date=note["meeting_date"],
            meeting_type=note["meeting_type"],
            note_text=note["note_text"],
        )
        for note in notes[:limit]
    ]


def build_customer_context(
    customer_id: str,
) -> CustomerInvestigationContext:
    notes = get_recent_meeting_notes(customer_id)

    return CustomerInvestigationContext(
        customer=get_customer_profile(customer_id),
        usage=get_usage_trend(customer_id),
        support=get_support_summary(customer_id),
        contract=get_contract_risk(customer_id),
        meeting_notes=notes,
        metadata={
            "source": "signalforge_sqlite",
            "meeting_note_count": len(notes),
        },
    )
