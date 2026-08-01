from __future__ import annotations

from src.models.specialist_findings import (
    AgentEvidence,
    SpecialistFinding,
)
from src.tools import get_usage_trend


def risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


class ProductAdoptionAgent:
    name = "product_adoption"

    def analyze(self, customer_id: str) -> SpecialistFinding:
        usage = get_usage_trend(customer_id)

        score = 0.0
        evidence: list[AgentEvidence] = []
        contradictions: list[str] = []

        if usage.active_user_change_pct <= -30:
            score += 45
        elif usage.active_user_change_pct <= -15:
            score += 30
        elif usage.active_user_change_pct <= -5:
            score += 15
        elif usage.active_user_change_pct >= 10:
            contradictions.append(
                "Active-user usage is growing rather than declining."
            )

        if usage.latest_seat_utilization < 0.40:
            score += 30
        elif usage.latest_seat_utilization < 0.60:
            score += 18
        elif usage.latest_seat_utilization >= 0.75:
            contradictions.append(
                "Seat utilization remains strong."
            )

        if usage.latest_feature_adoption < 0.35:
            score += 25
        elif usage.latest_feature_adoption < 0.55:
            score += 12
        elif usage.latest_feature_adoption >= 0.70:
            contradictions.append(
                "Core-feature adoption remains healthy."
            )

        score = min(score, 100)

        evidence.extend(
            [
                AgentEvidence(
                    source="usage_events",
                    signal="active_user_change",
                    value=f"{usage.active_user_change_pct:.1f}%",
                    explanation=(
                        "Change in active users between the two most "
                        "recent reporting periods."
                    ),
                ),
                AgentEvidence(
                    source="usage_events",
                    signal="seat_utilization",
                    value=f"{usage.latest_seat_utilization:.1%}",
                    explanation=(
                        "Share of purchased licenses currently being used."
                    ),
                ),
                AgentEvidence(
                    source="usage_events",
                    signal="feature_adoption",
                    value=f"{usage.latest_feature_adoption:.1%}",
                    explanation=(
                        "Average adoption of workflows connected to "
                        "customer value."
                    ),
                ),
            ]
        )

        return SpecialistFinding(
            customer_id=customer_id,
            agent_name=self.name,
            risk_score=round(score, 2),
            risk_level=risk_level(score),
            confidence=0.92,
            summary=(
                f"Product adoption risk is {risk_level(score)}. "
                f"Usage is {usage.trend_direction}, with "
                f"{usage.latest_seat_utilization:.0%} seat utilization."
            ),
            evidence=evidence,
            contradictory_signals=contradictions,
        )
