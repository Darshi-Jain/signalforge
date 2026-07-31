from src.tools.customer_tools import CustomerRepository
from src.orchestration.investigation import investigate

def test_high_risk_account_is_flagged():
    report = investigate(CustomerRepository().get_account("CUST-001"))
    assert report.risk_level in {"high", "critical"}
    assert report.churn_probability >= .60
    assert report.recommended_actions

def test_healthy_account_is_not_flagged():
    report = investigate(CustomerRepository().get_account("CUST-005"))
    assert report.risk_level in {"low", "medium"}
    assert report.health_score > 60

def test_seasonal_decline_is_validated():
    report = investigate(CustomerRepository().get_account("CUST-004"))
    assert report.contradictory_signals
