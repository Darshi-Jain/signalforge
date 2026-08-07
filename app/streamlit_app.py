from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agents import (
    CommercialRiskAgent,
    ProductAdoptionAgent,
    RelationshipIntelligenceAgent,
    SupportIntelligenceAgent,
    VoiceOfCustomerAgent,
)
from src.repositories import ContractRepository, CustomerRepository
from src.tools import (
    get_contract_risk,
    get_customer_profile,
    get_recent_meeting_notes,
    get_support_summary,
    get_usage_trend,
)


st.set_page_config(
    page_title="SignalForge",
    page_icon="📡",
    layout="wide",
)


RISK_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical",
}


def calculate_overall_risk(customer_id: str) -> dict:
    findings = [
        ProductAdoptionAgent().analyze(customer_id),
        SupportIntelligenceAgent().analyze(customer_id),
        RelationshipIntelligenceAgent().analyze(customer_id),
        CommercialRiskAgent().analyze(customer_id),
    ]

    weights = {
        "product_adoption": 0.30,
        "support_intelligence": 0.25,
        "relationship_intelligence": 0.25,
        "commercial_risk": 0.20,
    }

    score = sum(
        finding.risk_score * weights[finding.agent_name]
        for finding in findings
    )

    if score >= 80:
        level = "critical"
    elif score >= 60:
        level = "high"
    elif score >= 35:
        level = "medium"
    else:
        level = "low"

    return {
        "score": round(score, 1),
        "level": level,
        "findings": findings,
    }


@st.cache_data
def load_portfolio() -> pd.DataFrame:
    customers = CustomerRepository().list_customers(limit=500)
    contracts = ContractRepository().list_upcoming_renewals(days=3650)

    contract_map = {
        contract["customer_id"]: contract
        for contract in contracts
    }

    rows = []

    for customer in customers:
        contract = contract_map.get(customer["customer_id"], {})
        risk = calculate_overall_risk(customer["customer_id"])

        rows.append(
            {
                "customer_id": customer["customer_id"],
                "Customer": customer["customer_name"],
                "Segment": customer["segment"],
                "Industry": customer["industry"],
                "ARR": float(customer["arr"]),
                "Risk": RISK_LABELS[risk["level"]],
                "Risk Score": risk["score"],
                "Renewal Days": int(contract.get("renewal_days", 0)),
            }
        )

    return pd.DataFrame(rows)


def render_portfolio() -> None:
    st.title("SignalForge")
    st.caption("Agentic Customer Intelligence Platform")

    portfolio = load_portfolio()

    total_customers = len(portfolio)
    high_risk = len(
        portfolio[portfolio["Risk"].isin(["High", "Critical"])]
    )
    renewals_90 = len(portfolio[portfolio["Renewal Days"] <= 90])
    arr_at_risk = portfolio.loc[
        portfolio["Risk"].isin(["High", "Critical"]),
        "ARR",
    ].sum()

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Customers",
        f"{total_customers:,}",
    )
    metric_columns[1].metric(
        "High-Risk Accounts",
        f"{high_risk:,}",
    )
    metric_columns[2].metric(
        "Renewals Within 90 Days",
        f"{renewals_90:,}",
    )
    metric_columns[3].metric(
        "ARR at Risk",
        f"${arr_at_risk:,.0f}",
    )

    st.subheader("Customer Portfolio")

    risk_filter = st.multiselect(
        "Filter by risk",
        options=["Low", "Medium", "High", "Critical"],
        default=["Low", "Medium", "High", "Critical"],
    )

    filtered = portfolio[portfolio["Risk"].isin(risk_filter)].copy()
    filtered = filtered.sort_values(
        ["Risk Score", "ARR"],
        ascending=[False, False],
    )

    st.dataframe(
        filtered[
            [
                "Customer",
                "Segment",
                "Industry",
                "ARR",
                "Risk",
                "Risk Score",
                "Renewal Days",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ARR": st.column_config.NumberColumn(
                "ARR",
                format="$%.0f",
            ),
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Renewal Days": st.column_config.NumberColumn(
                "Renewal",
                format="%d days",
            ),
        },
    )


def render_customer_investigation() -> None:
    st.title("Customer Investigation")
    st.caption(
        "Review deterministic risk signals and AI-generated "
        "Voice of Customer insights."
    )

    customers = CustomerRepository().list_customers(limit=500)
    customer_options = {
        f"{customer['customer_name']} ({customer['customer_id']})":
            customer["customer_id"]
        for customer in customers
    }

    selected_label = st.selectbox(
        "Select a customer",
        options=list(customer_options.keys()),
    )
    customer_id = customer_options[selected_label]

    profile = get_customer_profile(customer_id)
    usage = get_usage_trend(customer_id)
    support = get_support_summary(customer_id)
    contract = get_contract_risk(customer_id)
    risk = calculate_overall_risk(customer_id)

    st.subheader(profile.customer_name)
    st.caption(
        f"{profile.segment} · {profile.industry} · "
        f"Owner: {profile.account_owner}"
    )

    metrics = st.columns(5)
    metrics[0].metric(
        "Overall Risk",
        RISK_LABELS[risk["level"]],
    )
    metrics[1].metric(
        "Risk Score",
        f"{risk['score']:.1f}/100",
    )
    metrics[2].metric(
        "ARR",
        f"${profile.arr:,.0f}",
    )
    metrics[3].metric(
        "Renewal",
        f"{contract.renewal_days} days",
    )
    metrics[4].metric(
        "Seat Utilization",
        f"{usage.latest_seat_utilization:.0%}",
    )

    st.divider()
    st.subheader("Specialist Risk Analysis")

    for finding in risk["findings"]:
        with st.expander(
            f"{finding.agent_name.replace('_', ' ').title()} "
            f"— {finding.risk_level.upper()} "
            f"({finding.risk_score:.1f})"
        ):
            st.write(finding.summary)

            evidence_rows = [
                {
                    "Signal": item.signal.replace("_", " ").title(),
                    "Value": item.value,
                    "Explanation": item.explanation,
                    "Source": item.source,
                }
                for item in finding.evidence
            ]

            st.dataframe(
                pd.DataFrame(evidence_rows),
                use_container_width=True,
                hide_index=True,
            )

            if finding.contradictory_signals:
                st.markdown("**Positive or contradictory signals**")
                for signal in finding.contradictory_signals:
                    st.write(f"• {signal}")

    st.divider()
    st.subheader("Voice of Customer")

    st.info(
        "Gemini runs only when you click the button below, "
        "which helps control AI usage and cost."
    )

    if st.button(
        "Run AI Voice of Customer Analysis",
        type="primary",
    ):
        with st.spinner("Analyzing customer meeting notes..."):
            try:
                result = VoiceOfCustomerAgent().analyze(customer_id)
                st.session_state["voice_result"] = result.model_dump()
                st.session_state["voice_customer"] = customer_id
            except Exception as error:
                st.error(f"AI analysis failed: {error}")

    result = st.session_state.get("voice_result")
    result_customer = st.session_state.get("voice_customer")

    if result and result_customer == customer_id:
        summary_columns = st.columns(3)
        summary_columns[0].metric(
            "Sentiment",
            result["sentiment"].title(),
        )
        summary_columns[1].metric(
            "Voice Risk",
            result["risk_level"].title(),
        )
        summary_columns[2].metric(
            "Confidence",
            f"{result['confidence']:.0%}",
        )

        st.write(result["summary"])

        indicators = {
            "Competitor mentioned": result["competitor_mentioned"],
            "Pricing objection": result["pricing_objection"],
            "Product gap detected": result["product_gap_detected"],
            "Churn language detected": result[
                "churn_language_detected"
            ],
        }

        st.markdown("**Detected signals**")
        for label, detected in indicators.items():
            marker = "⚠️" if detected else "✅"
            status = "Yes" if detected else "No"
            st.write(f"{marker} {label}: {status}")

        if result["evidence"]:
            st.markdown("**Supporting evidence**")

            for evidence in result["evidence"]:
                with st.expander(evidence["source_id"]):
                    st.write(evidence["evidence_text"])
                    st.caption(evidence["explanation"])

    st.divider()
    st.subheader("Recent Meeting Notes")

    meeting_notes = get_recent_meeting_notes(
        customer_id=customer_id,
        limit=5,
    )

    for note in meeting_notes:
        with st.expander(
            f"{note.meeting_date} · {note.meeting_type}"
        ):
            st.write(note.note_text)


def main() -> None:
    page = st.sidebar.radio(
        "Navigation",
        options=[
            "Portfolio Overview",
            "Customer Investigation",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "SignalForge combines deterministic customer analytics "
        "with Gemini-powered language interpretation."
    )

    if page == "Portfolio Overview":
        render_portfolio()
    else:
        render_customer_investigation()


if __name__ == "__main__":
    main()
