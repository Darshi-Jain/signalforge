from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TextEvidence(BaseModel):
    source_id: str
    evidence_text: str
    explanation: str


class VoiceOfCustomerFinding(BaseModel):
    customer_id: str
    sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    competitor_mentioned: bool
    pricing_objection: bool
    product_gap_detected: bool
    churn_language_detected: bool
    risk_level: Literal["low", "medium", "high", "critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    evidence: list[TextEvidence] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
