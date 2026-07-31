from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

RiskLevel = Literal["low", "medium", "high", "critical"]

class Evidence(BaseModel):
    source: str
    signal: str
    value: str
    explanation: str

class SpecialistFinding(BaseModel):
    agent: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]

class RecommendedAction(BaseModel):
    action: str
    owner: str
    due_in_days: int = Field(ge=0)
    rationale: str
    requires_approval: bool = True

class InvestigationReport(BaseModel):
    customer_id: str
    customer_name: str
    health_score: float = Field(ge=0, le=100)
    churn_probability: float = Field(ge=0, le=1)
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    arr_at_risk: float = Field(ge=0)
    renewal_days: int
    findings: list[SpecialistFinding]
    primary_drivers: list[str]
    contradictory_signals: list[str]
    recommended_actions: list[RecommendedAction]
