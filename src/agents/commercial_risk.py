from __future__ import annotations

from src.models.specialist_findings import (
    AgentEvidence,
    SpecialistFinding,
)
from src.tools import get_contract_risk


def risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


class CommercialRiskAgent:
    name = "commercial_risk"

    def analyze(self, customer_id: str) -> SpecialistFinding:
        contract = get_contract_risk(customer_id)

        score = 0.0
        contradictions: list[str] = []

        if contract.renewal_days <= 30:
            score += 35
        elif contract.renewal_days <= 60:
            score += 25
        elif contract.renewal_days <= 90:
            score += 15

        if contract.payment_status == "Delayed":
            score += 25
        elif contract.payment_status == "Current":
            contradictions.append(
                "The account is current on payments."
            )

        if contract.requested_seat_reduction_pct > 0:
            score += min(
                contract.requested_seat_reduction_pct * 1.2,
                30,
            )

        if contract.pricing_objection:
            score += 20

        score = min(score, 100)

        evidence = [
            AgentEvidence(
                source="contracts",
                signal="renewal_days",
                value=str(contract.renewal_days),
                explanation="Days remaining before contract renewal.",
            ),
            AgentEvidence(
                source="contracts",
                signal="payment_status",
                value=contract.payment_status,
                explanation="Current commercial payment status.",
            ),
            AgentEvidence(
                source="contracts",
                signal="requested_seat_reduction",
                value=f"{contract.requested_seat_reduction_pct:.0f}%",
                explanation=(
                    "Requested reduction in purchased licenses."
                ),
            ),
            AgentEvidence(
                source="contracts",
                signal="pricing_objection",
                value=str(contract.pricing_objection),
                explanation=(
                    "Whether pricing concerns are documented."
                ),
            ),
        ]

        return SpecialistFinding(
            customer_id=customer_id,
            agent_name=self.name,
            risk_score=round(score, 2),
            risk_level=risk_level(score),
            confidence=0.94,
            summary=(
                f"Commercial risk is {risk_level(score)} with renewal "
                f"in {contract.renewal_days} days and "
                f"${contract.arr:,.0f} ARR."
            ),
            evidence=evidence,
            contradictory_signals=contradictions,
        )
