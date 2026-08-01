from __future__ import annotations

from src.models.specialist_findings import (
    AgentEvidence,
    SpecialistFinding,
)
from src.tools import get_support_summary


def risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


class SupportIntelligenceAgent:
    name = "support_intelligence"

    def analyze(self, customer_id: str) -> SpecialistFinding:
        support = get_support_summary(customer_id)

        score = 0.0
        contradictions: list[str] = []

        score += min(support.critical_tickets * 18, 45)
        score += min(support.reopened_tickets * 12, 30)
        score += min(support.unresolved_tickets * 8, 20)

        if support.average_resolution_hours >= 48:
            score += 20
        elif support.average_resolution_hours >= 24:
            score += 10
        elif support.average_resolution_hours <= 8:
            contradictions.append(
                "Support issues are being resolved quickly."
            )

        if support.total_tickets <= 2:
            contradictions.append(
                "Overall support volume is low."
            )

        score = min(score, 100)

        evidence = [
            AgentEvidence(
                source="support_tickets",
                signal="critical_tickets",
                value=str(support.critical_tickets),
                explanation="Number of P1 support cases.",
            ),
            AgentEvidence(
                source="support_tickets",
                signal="reopened_tickets",
                value=str(support.reopened_tickets),
                explanation=(
                    "Reopened cases may indicate unresolved root causes."
                ),
            ),
            AgentEvidence(
                source="support_tickets",
                signal="unresolved_tickets",
                value=str(support.unresolved_tickets),
                explanation="Open or escalated customer cases.",
            ),
            AgentEvidence(
                source="support_tickets",
                signal="average_resolution_hours",
                value=f"{support.average_resolution_hours:.1f}",
                explanation="Average time required to resolve cases.",
            ),
        ]

        return SpecialistFinding(
            customer_id=customer_id,
            agent_name=self.name,
            risk_score=round(score, 2),
            risk_level=risk_level(score),
            confidence=0.90,
            summary=(
                f"Support risk is {risk_level(score)}. "
                f"The account has {support.critical_tickets} critical, "
                f"{support.reopened_tickets} reopened, and "
                f"{support.unresolved_tickets} unresolved cases."
            ),
            evidence=evidence,
            contradictory_signals=contradictions,
        )
