from __future__ import annotations

from src.agents import (
    CommercialRiskAgent,
    ProductAdoptionAgent,
    RelationshipIntelligenceAgent,
    SupportIntelligenceAgent,
    VoiceOfCustomerAgent,
)

RISK_VALUES = {
    "low": 20.0,
    "medium": 50.0,
    "high": 75.0,
    "critical": 95.0,
}


def _risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def investigate_customer(customer_id: str) -> dict:
    product = ProductAdoptionAgent().analyze(customer_id)
    support = SupportIntelligenceAgent().analyze(customer_id)
    relationship = RelationshipIntelligenceAgent().analyze(customer_id)
    commercial = CommercialRiskAgent().analyze(customer_id)
    voice = VoiceOfCustomerAgent().analyze(customer_id)

    weighted_score = (
        product.risk_score * 0.25
        + support.risk_score * 0.20
        + relationship.risk_score * 0.20
        + commercial.risk_score * 0.20
        + RISK_VALUES[voice.risk_level] * 0.15
    )

    findings = sorted(
        [product, support, relationship, commercial],
        key=lambda item: item.risk_score,
        reverse=True,
    )

    contradictions = [
        signal
        for finding in findings
        for signal in finding.contradictory_signals
    ]

    actions = []

    if product.risk_score >= 35:
        actions.append("Run a targeted product-adoption review.")

    if support.risk_score >= 35:
        actions.append("Open a technical root-cause review.")

    if relationship.risk_score >= 35:
        actions.append(
            "Rebuild stakeholder coverage and executive sponsorship."
        )

    if commercial.risk_score >= 35:
        actions.append("Create a renewal recovery plan.")

    if (
        voice.competitor_mentioned
        or voice.pricing_objection
        or voice.product_gap_detected
        or voice.churn_language_detected
    ):
        actions.append(
            "Prepare an evidence-based objection and retention response plan."
        )

    if not actions:
        actions.append(
            "Maintain the current success plan and explore expansion."
        )

    return {
        "customer_id": customer_id,
        "overall_risk_score": round(weighted_score, 1),
        "overall_risk": _risk_level(weighted_score),
        "specialist_findings": [
            finding.model_dump()
            for finding in findings
        ],
        "voice_of_customer": voice.model_dump(),
        "contradictory_signals": contradictions,
        "recommended_actions": actions,
    }
