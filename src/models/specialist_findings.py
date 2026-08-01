from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high", "critical"]


class AgentEvidence(BaseModel):
    source: str
    signal: str
    value: str
    explanation: str


class SpecialistFinding(BaseModel):
    customer_id: str
    agent_name: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[AgentEvidence] = Field(default_factory=list)
    contradictory_signals: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
