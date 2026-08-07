from __future__ import annotations

from pathlib import Path

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
    page_icon="⚡",
    layout="wide",
)


def load_css() -> None:
    css_path = Path("app/styles.css")
    st.markdown(
        f"<style>{css_path.read_text()}</style>",
        unsafe_allow_html=True,
    )


load_css()


RISK_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical",
}


def risk_level(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


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

    return {
        "score": round(score, 1),
        "level": risk_level(score),
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


def metric_card(label: str, value: str, foot: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    st.markdown(
        """
        <div class="sf-brand">
            <h1>SignalForge ⚡</h1>
        </div>
        <div class="sf-subtitle">
            Agentic Customer Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_portfolio() -> None:
    render_brand()

    portfolio = load_portfolio()

    total_customers = len(portfolio)
    high_risk = len(
        portfolio[portfolio["Risk"].isin(["High", "Critical"])]
    )
    renewals_90 = len(
        portfolio[portfolio["Renewal Days"] <= 90]
    )
    arr_at_risk = portfolio.loc[
        portfolio["Risk"].isin(["High", "Critical"]),
        "ARR",
    ].sum()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Customers",
            f"{total_customers:,}",
            "Active portfolio",
        )

    with c2:
        metric_card(
            "High-Risk Accounts",
            f"{high_risk:,}",
            "Requires proactive attention",
        )

    with c3:
        metric_card(
            "Renewals (90 Days)",
            f"{renewals_90:,}",
            "Upcoming renewal window",
        )

    with c4:
        metric_card(
            "ARR at Risk",
            f"${arr_at_risk:,.0f}",
            "Revenue exposed to churn risk",
        )

    st.markdown(
        """
        <div class="portfolio-card">
            <div class="section-title">Customer Portfolio</div>
            <div class="section-subtitle">
                Monitor customer health and risk across your portfolio
            </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, filter_col, sort_col = st.columns([2, 2, 1.5])

    with search_col:
        search = st.text_input(
            "Search customers",
            placeholder="Search by customer name",
        )

    with filter_col:
        selected_risks = st.multiselect(
            "Filter by risk",
            options=["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"],
        )

    with sort_col:
        sort_option = st.selectbox(
            "Sort by",
            options=[
                "Risk Score: High to Low",
                "ARR: High to Low",
                "Renewal: Soonest",
            ],
        )

    filtered = portfolio[
        portfolio["Risk"].isin(selected_risks)
    ].copy()

    if search:
        filtered = filtered[
            filtered["Customer"].str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    if sort_option == "Risk Score: High to Low":
        filtered = filtered.sort_values(
            ["Risk Score", "ARR"],
            ascending=[False, False],
        )
    elif sort_option == "ARR: High to Low":
        filtered = filtered.sort_values(
            "ARR",
            ascending=False,
        )
    else:
        filtered = filtered.sort_values(
            "Renewal Days",
            ascending=True,
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

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="ai-banner">
            ✨ Tip: Open the Investigation page to run a full
            AI-powered customer analysis with evidence and recommendations.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_investigation() -> None:
    render_brand()

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

    st.markdown(
        f"""
        <div class="portfolio-card">
            <div class="section-title">{profile.customer_name}</div>
            <div class="section-subtitle">
                {profile.segment} · {profile.industry} ·
                Owner: {profile.account_owner}
            </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        metric_card(
            "Overall Risk",
            RISK_LABELS[risk["level"]],
            f"{risk['score']:.1f}/100",
        )

    with c2:
        metric_card(
            "ARR",
            f"${profile.arr:,.0f}",
            "Annual recurring revenue",
        )

    with c3:
        metric_card(
            "Renewal",
            f"{contract.renewal_days} days",
            contract.urgency.title(),
        )

    with c4:
        metric_card(
            "Seat Utilization",
            f"{usage.latest_seat_utilization:.0%}",
            usage.trend_direction.title(),
        )

    with c5:
        metric_card(
            "Support Tickets",
            f"{support.total_tickets}",
            f"{support.critical_tickets} critical",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Specialist Analysis")

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
                }
                for item in finding.evidence
            ]

            st.dataframe(
                pd.DataFrame(evidence_rows),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown("### AI Voice of Customer")

    st.caption(
        "Gemini runs only when requested to keep AI usage controlled."
    )

    if st.button(
        "Run AI Investigation",
        type="primary",
        use_container_width=False,
    ):
        with st.spinner(
            "Gemini is analyzing customer meeting notes..."
        ):
            try:
                result = VoiceOfCustomerAgent().analyze(customer_id)
                st.session_state["voice_result"] = result.model_dump()
                st.session_state["voice_customer"] = customer_id
            except Exception as error:
                st.error(f"AI analysis failed: {error}")

    result = st.session_state.get("voice_result")
    result_customer = st.session_state.get("voice_customer")

    if result and result_customer == customer_id:
        st.markdown(
            '<div class="investigation-card">',
            unsafe_allow_html=True,
        )

        v1, v2, v3 = st.columns(3)
        v1.metric("Sentiment", result["sentiment"].title())
        v2.metric("Voice Risk", result["risk_level"].title())
        v3.metric("Confidence", f"{result['confidence']:.0%}")

        st.write(result["summary"])

        st.markdown("**Detected signals**")

        signal_map = {
            "Competitor mentioned": result["competitor_mentioned"],
            "Pricing objection": result["pricing_objection"],
            "Product gap": result["product_gap_detected"],
            "Churn language": result["churn_language_detected"],
        }

        for label, detected in signal_map.items():
            icon = "⚠️" if detected else "✓"
            st.write(f"{icon} {label}: {'Yes' if detected else 'No'}")

        if result["evidence"]:
            st.markdown("**Supporting evidence**")

            for evidence in result["evidence"]:
                with st.expander(evidence["source_id"]):
                    st.write(evidence["evidence_text"])
                    st.caption(evidence["explanation"])

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Recent Meeting Notes")

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
    with st.sidebar:
        st.markdown("## ⚡ SignalForge")
        st.caption("Customer Intelligence")

        page = st.radio(
            "Navigation",
            options=[
                "Portfolio",
                "Investigation",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption("AI Agents")
        st.success("5 / 5 systems active")

    if page == "Portfolio":
        render_portfolio()
    else:
        render_investigation()


if __name__ == "__main__":
    main()
