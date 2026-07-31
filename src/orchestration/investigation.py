from __future__ import annotations
from src.agents.specialists import adoption_finding, support_finding, relationship_finding, commercial_finding, sentiment_finding
from src.models.schemas import InvestigationReport, RecommendedAction

WEIGHTS = {"product_adoption": .30, "support_intelligence": .15, "relationship_intelligence": .20, "commercial_risk": .20, "voice_of_customer": .15}

def _level(prob: float) -> str:
    if prob >= .80: return "critical"
    if prob >= .60: return "high"
    if prob >= .35: return "medium"
    return "low"

def investigate(account: dict) -> InvestigationReport:
    findings = [adoption_finding(account), support_finding(account), relationship_finding(account), commercial_finding(account), sentiment_finding(account)]
    risk = sum(f.risk_score * WEIGHTS[f.agent] for f in findings)
    # Validation adjustment: documented seasonality reduces usage-driven false positives.
    contradictions = []
    if int(account.get("seasonal_decline", 0)):
        risk = max(0, risk - 10)
        contradictions.append("Usage decline overlaps with a documented seasonal slowdown.")
    probability = min(.98, max(.02, risk / 100))
    drivers = []
    for finding in sorted(findings, key=lambda x: x.risk_score, reverse=True)[:3]:
        top = max(finding.evidence, key=lambda e: len(e.explanation))
        drivers.append(f"{finding.agent}: {top.signal} ({top.value})")
    actions = _actions(findings, account)
    return InvestigationReport(
        customer_id=account["customer_id"], customer_name=account["customer_name"],
        health_score=round(100-risk,1), churn_probability=round(probability,3), risk_level=_level(probability),
        confidence=round(sum(f.confidence for f in findings)/len(findings),2), arr_at_risk=float(account["arr"]),
        renewal_days=int(account["renewal_days"]), findings=findings, primary_drivers=drivers,
        contradictory_signals=contradictions, recommended_actions=actions)

def _actions(findings, a):
    by_name = {f.agent:f for f in findings}
    actions=[]
    if by_name["product_adoption"].risk_score >= 45:
        actions.append(RecommendedAction(action="Run a targeted adoption and workflow review", owner="CSM + Solutions Engineer", due_in_days=7, rationale="Product usage and core-feature adoption show deterioration."))
    if by_name["support_intelligence"].risk_score >= 45:
        actions.append(RecommendedAction(action="Open a technical root-cause review for recurring issues", owner="Support Lead", due_in_days=3, rationale="Critical or reopened cases may be blocking customer value."))
    if by_name["relationship_intelligence"].risk_score >= 45:
        actions.append(RecommendedAction(action="Rebuild the stakeholder map and secure an executive sponsor", owner="CSM", due_in_days=7, rationale="Relationship coverage or executive engagement is weak."))
    if int(a["renewal_days"]) <= 90:
        actions.append(RecommendedAction(action="Create a renewal recovery plan with weekly checkpoints", owner="CSM + Account Executive", due_in_days=2, rationale="Renewal proximity increases urgency."))
    if not actions:
        actions.append(RecommendedAction(action="Continue monitoring and review signals in 30 days", owner="CSM", due_in_days=30, rationale="No material risk cluster currently requires escalation."))
    return actions
