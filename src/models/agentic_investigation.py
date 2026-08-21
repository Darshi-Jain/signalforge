from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RiskDriver(BaseModel):
    domain: str
    severity: str
    explanation: str
    evidence: list[str] = Field(default_factory=list)


class RecommendedAction(BaseModel):
    priority: int
    action: str
    owner: str
    rationale: str


class AgenticInvestigation(BaseModel):
    customer_id: str

    overall_risk: Literal["Low", "Medium", "High"]
    overall_risk_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

    executive_summary: str

    risk_drivers: list[RiskDriver] = Field(default_factory=list)

    positive_signals: list[str] = Field(default_factory=list)
    contradictory_signals: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

    recommended_actions: list[RecommendedAction] = Field(
        default_factory=list
    )

    specialists_consulted: list[str] = Field(default_factory=list)
