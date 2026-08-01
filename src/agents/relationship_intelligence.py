from __future__ import annotations

from datetime import date

from src.models.specialist_findings import (
    AgentEvidence,
    SpecialistFinding,
)
from src.repositories import RelationshipRepository


def risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


class RelationshipIntelligenceAgent:
    name = "relationship_intelligence"

    def analyze(self, customer_id: str) -> SpecialistFinding:
        repository = RelationshipRepository()
        summary = repository.get_summary(customer_id)

        if summary is None:
            raise ValueError(
                f"No relationship data found for: {customer_id}"
            )

        no_response_count = repository.get_no_response_count(customer_id)
        score = 0.0
        contradictions: list[str] = []
        missing: list[str] = []

        active_champions = int(summary["active_champions"] or 0)
        active_executives = int(
            summary["active_executive_sponsors"] or 0
        )
        active_stakeholders = int(summary["active_stakeholders"] or 0)
        latest_engagement = summary["latest_engagement_date"]

        if active_champions == 0:
            score += 35
        else:
            contradictions.append(
                "An active customer champion is present."
            )

        if active_executives == 0:
            score += 25
        else:
            contradictions.append(
                "An active executive sponsor is present."
            )

        if active_stakeholders <= 1:
            score += 15

        engagement_days = None
        if latest_engagement:
            engagement_date = date.fromisoformat(latest_engagement)
            engagement_days = (date.today() - engagement_date).days

            if engagement_days >= 90:
                score += 25
            elif engagement_days >= 60:
                score += 15
            elif engagement_days <= 30:
                contradictions.append(
                    "The account has recent stakeholder engagement."
                )
        else:
            missing.append("No stakeholder engagement date is available.")
            score += 10

        score += min(no_response_count * 5, 20)
        score = min(score, 100)

        evidence = [
            AgentEvidence(
                source="stakeholders",
                signal="active_champions",
                value=str(active_champions),
                explanation="Number of active customer champions.",
            ),
            AgentEvidence(
                source="stakeholders",
                signal="active_executive_sponsors",
                value=str(active_executives),
                explanation="Number of active executive sponsors.",
            ),
            AgentEvidence(
                source="stakeholders",
                signal="active_stakeholders",
                value=str(active_stakeholders),
                explanation="Number of active customer contacts.",
            ),
            AgentEvidence(
                source="crm_activities",
                signal="no_response_count",
                value=str(no_response_count),
                explanation=(
                    "Customer activities that received no response."
                ),
            ),
            AgentEvidence(
                source="stakeholders",
                signal="days_since_engagement",
                value=(
                    str(engagement_days)
                    if engagement_days is not None
                    else "unknown"
                ),
                explanation=(
                    "Days since the latest recorded stakeholder engagement."
                ),
            ),
        ]

        return SpecialistFinding(
            customer_id=customer_id,
            agent_name=self.name,
            risk_score=round(score, 2),
            risk_level=risk_level(score),
            confidence=0.88,
            summary=(
                f"Relationship risk is {risk_level(score)}. "
                f"The account has {active_champions} active champion(s), "
                f"{active_executives} active executive sponsor(s), and "
                f"{no_response_count} unanswered activities."
            ),
            evidence=evidence,
            contradictory_signals=contradictions,
            missing_information=missing,
        )
