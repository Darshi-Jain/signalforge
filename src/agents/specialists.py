from __future__ import annotations
from src.models.schemas import Evidence, SpecialistFinding

def _level(score: float) -> str:
    if score >= 80: return "critical"
    if score >= 60: return "high"
    if score >= 35: return "medium"
    return "low"

def adoption_finding(a: dict) -> SpecialistFinding:
    decline = max(0.0, -float(a["usage_change_pct"]))
    utilization_gap = max(0.0, 70 - float(a["seat_utilization_pct"]))
    feature_gap = max(0.0, 65 - float(a["core_feature_adoption_pct"]))
    score = min(100, decline * 1.3 + utilization_gap * .7 + feature_gap * .5)
    evidence = [
        Evidence(source="usage_metrics", signal="usage_change", value=f'{a["usage_change_pct"]}%', explanation="Recent change in active product usage."),
        Evidence(source="usage_metrics", signal="seat_utilization", value=f'{a["seat_utilization_pct"]}%', explanation="Share of purchased seats actively used."),
        Evidence(source="usage_metrics", signal="core_feature_adoption", value=f'{a["core_feature_adoption_pct"]}%', explanation="Adoption of workflows tied to customer value."),
    ]
    return SpecialistFinding(agent="product_adoption", risk_score=round(score,1), risk_level=_level(score), confidence=.90, evidence=evidence)

def support_finding(a: dict) -> SpecialistFinding:
    score = min(100, float(a["critical_tickets_30d"]) * 18 + float(a["reopened_tickets_30d"]) * 12 + max(0, float(a["avg_resolution_hours"])-16) * 1.2)
    evidence = [
        Evidence(source="support_metrics", signal="critical_tickets", value=str(a["critical_tickets_30d"]), explanation="Critical cases opened in the last 30 days."),
        Evidence(source="support_metrics", signal="reopened_tickets", value=str(a["reopened_tickets_30d"]), explanation="Repeated issues may indicate unresolved root causes."),
        Evidence(source="support_metrics", signal="resolution_time", value=f'{a["avg_resolution_hours"]} hours', explanation="Average time to resolve customer issues."),
    ]
    return SpecialistFinding(agent="support_intelligence", risk_score=round(score,1), risk_level=_level(score), confidence=.86, evidence=evidence)

def relationship_finding(a: dict) -> SpecialistFinding:
    score = min(100, max(0, float(a["days_since_exec_meeting"])-30) * .7 + int(a["champion_left"]) * 35 + float(a["missed_meetings_60d"]) * 10)
    evidence = [
        Evidence(source="engagement_metrics", signal="executive_engagement", value=f'{a["days_since_exec_meeting"]} days', explanation="Days since the last executive-level customer meeting."),
        Evidence(source="engagement_metrics", signal="champion_left", value=str(bool(a["champion_left"])), explanation="Loss of a champion increases relationship risk."),
        Evidence(source="engagement_metrics", signal="missed_meetings", value=str(a["missed_meetings_60d"]), explanation="Missed meetings in the last 60 days."),
    ]
    return SpecialistFinding(agent="relationship_intelligence", risk_score=round(score,1), risk_level=_level(score), confidence=.84, evidence=evidence)

def commercial_finding(a: dict) -> SpecialistFinding:
    renewal = int(a["renewal_days"])
    urgency = max(0, 120-renewal) * .45
    score = min(100, urgency + int(a["payment_delayed"]) * 25 + max(0, float(a["requested_seat_reduction_pct"])) * 1.2)
    evidence = [
        Evidence(source="customers", signal="renewal_days", value=str(renewal), explanation="Days remaining until contract renewal."),
        Evidence(source="customers", signal="payment_delayed", value=str(bool(a["payment_delayed"])), explanation="Delayed payment can indicate commercial friction."),
        Evidence(source="customers", signal="seat_reduction_request", value=f'{a["requested_seat_reduction_pct"]}%', explanation="Requested contraction in licensed seats."),
    ]
    return SpecialistFinding(agent="commercial_risk", risk_score=round(score,1), risk_level=_level(score), confidence=.88, evidence=evidence)

def sentiment_finding(a: dict) -> SpecialistFinding:
    score = min(100, max(0, -float(a["sentiment_score"])) * 70 + int(a["competitor_mentioned"]) * 30 + int(a["pricing_objection"]) * 15)
    evidence = [
        Evidence(source="sentiment_metrics", signal="sentiment", value=str(a["sentiment_score"]), explanation="Aggregated sentiment from synthetic notes and feedback."),
        Evidence(source="sentiment_metrics", signal="competitor_mentioned", value=str(bool(a["competitor_mentioned"])), explanation="Customer has mentioned evaluating another provider."),
        Evidence(source="sentiment_metrics", signal="pricing_objection", value=str(bool(a["pricing_objection"])), explanation="Pricing concerns were detected in account context."),
    ]
    return SpecialistFinding(agent="voice_of_customer", risk_score=round(score,1), risk_level=_level(score), confidence=.80, evidence=evidence)
