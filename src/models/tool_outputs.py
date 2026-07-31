from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    customer_id: str
    customer_name: str
    industry: str
    segment: str
    arr: float
    account_owner: str
    lifecycle_stage: str
    risk_profile: str


class UsageTrend(BaseModel):
    customer_id: str
    months_available: int
    latest_active_users: float
    previous_active_users: float
    active_user_change_pct: float
    latest_seat_utilization: float
    latest_feature_adoption: float
    latest_api_calls: int
    trend_direction: str


class SupportSummary(BaseModel):
    customer_id: str
    total_tickets: int
    critical_tickets: int
    reopened_tickets: int
    unresolved_tickets: int
    average_resolution_hours: float


class ContractRisk(BaseModel):
    customer_id: str
    renewal_date: str
    renewal_days: int
    arr: float
    payment_status: str
    requested_seat_reduction_pct: float
    pricing_objection: bool
    urgency: str


class MeetingEvidence(BaseModel):
    note_id: str
    meeting_date: str
    meeting_type: str
    note_text: str


class CustomerInvestigationContext(BaseModel):
    customer: CustomerProfile
    usage: UsageTrend
    support: SupportSummary
    contract: ContractRisk
    meeting_notes: list[MeetingEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
