from __future__ import annotations

from src.agents import (
    CommercialRiskAgent,
    ProductAdoptionAgent,
    RelationshipIntelligenceAgent,
    SupportIntelligenceAgent,
)


WEIGHTS = {
    "product_adoption": 0.30,
    "support_intelligence": 0.25,
    "relationship_intelligence": 0.25,
    "commercial_risk": 0.20,
}


def risk_level(score: float) -> str:
    if score >= 60:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def calculate_customer_risk(customer_id: str) -> dict:
    findings = [
        ProductAdoptionAgent().analyze(customer_id),
        SupportIntelligenceAgent().analyze(customer_id),
        RelationshipIntelligenceAgent().analyze(customer_id),
        CommercialRiskAgent().analyze(customer_id),
    ]

    weighted_average = sum(
        finding.risk_score * WEIGHTS[finding.agent_name]
        for finding in findings
    )

    strongest_signal = max(
        finding.risk_score
        for finding in findings
    )

    # Prevent one severe customer signal from being hidden
    # inside an otherwise healthy average.
    calibrated_score = (
        weighted_average * 0.65
        + strongest_signal * 0.35
    )

    calibrated_score = round(
        min(calibrated_score, 100),
        1,
    )

    return {
        "score": calibrated_score,
        "level": risk_level(calibrated_score),
        "findings": sorted(
            findings,
            key=lambda finding: finding.risk_score,
            reverse=True,
        ),
        "weighted_average": round(weighted_average, 1),
        "strongest_signal": round(strongest_signal, 1),
    }
