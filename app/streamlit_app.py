from __future__ import annotations

import html
from pathlib import Path

import pandas as pd
import streamlit as st

from src.repositories import ContractRepository, CustomerRepository
from src.services import calculate_customer_risk
from src.tools import (
    get_contract_risk,
    get_customer_profile,
    get_recent_meeting_notes,
    get_support_summary,
    get_usage_trend,
)
from src.workflows import investigate_customer


st.set_page_config(
    page_title="SignalForge",
    page_icon="⚡",
    layout="wide",
)


def load_css() -> None:
    css = Path("app/styles.css").read_text()
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


load_css()


RISK_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Critical",
}

RISK_COLORS = {
    "Low": "#16a34a",
    "Medium": "#f59e0b",
    "High": "#f97316",
    "Critical": "#dc2626",
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
        risk = calculate_customer_risk(customer["customer_id"])
        contract = contract_map.get(customer["customer_id"], {})

        rows.append(
            {
                "customer_id": customer["customer_id"],
                "Customer": customer["customer_name"],
                "Segment": customer["segment"],
                "Industry": customer["industry"],
                "ARR": float(customer["arr"]),
                "Risk": RISK_LABELS[risk["level"]],
                "Risk Score": float(risk["score"]),
                "Renewal Days": int(
                    contract.get("renewal_days", 0)
                ),
            }
        )

    return pd.DataFrame(rows)


def metric_card(
    icon: str,
    icon_class: str,
    label: str,
    value: str,
    foot: str,
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-icon {icon_class}">{icon}</div>
                <div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            </div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    st.markdown(
        """
        <div class="sf-brand">
            <h1>SignalForge <span>⚡</span></h1>
            <div class="sf-subtitle">
                Agentic Customer Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(risk: str) -> str:
    css_class = risk.lower()
    return (
        f'<span class="risk-pill risk-{css_class}">'
        f'{html.escape(risk)}</span>'
    )


def portfolio_table(data: pd.DataFrame) -> str:
    rows = []

    for _, item in data.iterrows():
        score = float(item["Risk Score"])
        risk = item["Risk"]
        color = RISK_COLORS[risk]
        customer = html.escape(str(item["Customer"]))
        segment = html.escape(str(item["Segment"]))
        industry = html.escape(str(item["Industry"]))
        initials = html.escape(str(item["Customer"])[-2:])

        row = (
            "<tr>"
            f'<td class="customer-cell">'
            f'<div class="customer-avatar">{initials}</div>'
            f"{customer}</td>"
            f"<td>{segment}</td>"
            f"<td>{industry}</td>"
            f'<td>${float(item["ARR"]):,.0f}</td>'
            f"<td>{risk_badge(risk)}</td>"
            '<td><div class="risk-score-wrap">'
            '<div class="risk-track">'
            f'<div class="risk-fill" style="width:{score}%;background:{color};"></div>'
            "</div>"
            f"<span>{score:.1f}</span>"
            "</div></td>"
            f'<td>📅 {int(item["Renewal Days"])} days</td>'
            "</tr>"
        )

        rows.append(row)

    return (
        '<div class="table-shell">'
        '<table class="sf-table">'
        "<thead><tr>"
        "<th>Customer</th>"
        "<th>Segment</th>"
        "<th>Industry</th>"
        "<th>ARR</th>"
        "<th>Risk</th>"
        "<th>Risk Score</th>"
        "<th>Renewal</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
    )

def render_portfolio() -> None:
    render_brand()
    portfolio = load_portfolio()

    high_mask = portfolio["Risk"].isin(
        ["High", "Critical"]
    )

    total_customers = len(portfolio)
    high_risk = int(high_mask.sum())
    renewals_90 = int(
        (portfolio["Renewal Days"] <= 90).sum()
    )
    arr_at_risk = float(
        portfolio.loc[high_mask, "ARR"].sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "👥",
            "icon-blue",
            "Total Customers",
            f"{total_customers:,}",
            "Active portfolio",
        )

    with c2:
        metric_card(
            "🛡",
            "icon-red",
            "High-Risk Accounts",
            f"{high_risk:,}",
            "Requires proactive attention",
        )

    with c3:
        metric_card(
            "📅",
            "icon-purple",
            "Renewals (90 Days)",
            f"{renewals_90:,}",
            "Upcoming renewal window",
        )

    with c4:
        metric_card(
            "$",
            "icon-green",
            "ARR at Risk",
            f"${arr_at_risk:,.0f}",
            "Revenue exposed to churn risk",
        )

    st.markdown(
        """
        <div class="portfolio-heading">
            <div class="section-title">Customer Portfolio</div>
            <div class="section-subtitle">
                Monitor customer health and prioritize accounts
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, risk_col, sort_col = st.columns(
        [1.5, 1.6, 1.2]
    )

    with search_col:
        search = st.text_input(
            "Search customers",
            placeholder="Search by customer name",
        )

    with risk_col:
        selected_risks = st.multiselect(
            "Filter by risk",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"],
        )

    with sort_col:
        sort_option = st.selectbox(
            "Sort by",
            [
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

    page_size = 10
    page_count = max(
        1,
        (len(filtered) + page_size - 1) // page_size,
    )

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=page_count,
        value=1,
        step=1,
        label_visibility="collapsed",
    )

    start = (int(page) - 1) * page_size
    end = start + page_size
    displayed = filtered.iloc[start:end]

    st.markdown(
        portfolio_table(displayed),
        unsafe_allow_html=True,
    )

    footer_left, footer_right = st.columns([3, 1])

    with footer_left:
        st.caption(
            f"Showing {start + 1 if len(filtered) else 0} "
            f"to {min(end, len(filtered))} "
            f"of {len(filtered)} customers"
        )

    with footer_right:
        st.caption(
            f"Page {int(page)} of {page_count}"
        )

    st.markdown(
        """
        <div class="ai-banner">
            ✨ <strong>Tip:</strong> Open Investigation to run a
            full AI-powered account analysis with evidence and
            recommended next actions.
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_bar(title: str, finding: dict) -> None:
    risk = finding["risk_level"].title()
    score = float(finding["risk_score"])
    color = RISK_COLORS[RISK_LABELS[finding["risk_level"]]]

    st.markdown(
        f"""
        <div class="risk-analysis-row">
            <div class="risk-analysis-name">{html.escape(title)}</div>
            <div class="risk-analysis-track">
                <div
                    class="risk-analysis-fill"
                    style="width:{score}%;background:{color};"
                ></div>
            </div>
            <div class="risk-analysis-score">{score:.0f}</div>
            <div>{risk_badge(risk)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_investigation() -> None:
    render_brand()

    customers = CustomerRepository().list_customers(limit=500)

    options = {
        f"{c['customer_name']} ({c['customer_id']})":
            c["customer_id"]
        for c in customers
    }

    selected = st.selectbox(
        "Select customer",
        list(options.keys()),
    )
    customer_id = options[selected]

    profile = get_customer_profile(customer_id)
    usage = get_usage_trend(customer_id)
    support = get_support_summary(customer_id)
    contract = get_contract_risk(customer_id)
    risk = calculate_customer_risk(customer_id)

    top_left, top_right = st.columns([3, 1])

    with top_left:
        st.markdown(
            f"""
            <div class="customer-title">
                {html.escape(profile.customer_name)}
            </div>
            <div class="customer-meta">
                {html.escape(profile.industry)} ·
                {html.escape(profile.segment)} ·
                Owner: {html.escape(profile.account_owner)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            f"""
            <div class="hero-risk">
                {risk_badge(RISK_LABELS[risk["level"]])}
                <strong>{risk["score"]:.1f} / 100</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        metric_card(
            "$",
            "icon-green",
            "ARR",
            f"${profile.arr:,.0f}",
            "Annual recurring revenue",
        )

    with m2:
        metric_card(
            "📅",
            "icon-purple",
            "Renewal",
            f"{contract.renewal_days} days",
            contract.urgency.title(),
        )

    with m3:
        metric_card(
            "📈",
            "icon-blue",
            "Seat Utilization",
            f"{usage.latest_seat_utilization:.0%}",
            usage.trend_direction.title(),
        )

    with m4:
        metric_card(
            "🎫",
            "icon-red",
            "Support",
            str(support.total_tickets),
            f"{support.critical_tickets} critical",
        )

    st.markdown("### Why this customer needs attention")

    names = {
        "product_adoption": "Product Adoption",
        "support_intelligence": "Support",
        "relationship_intelligence": "Relationship",
        "commercial_risk": "Commercial",
    }

    for finding in risk["findings"]:
        risk_bar(
            names[finding.agent_name],
            finding.model_dump(),
        )

    st.markdown("### ✨ AI Customer Investigation")

    st.caption(
        "Gemini analyzes the customer's meeting notes and "
        "combines them with SignalForge's account-risk agents."
    )

    if st.button(
        "Run Full AI Investigation",
        type="primary",
    ):
        with st.spinner(
            "Running SignalForge agents and Gemini analysis..."
        ):
            try:
                result = investigate_customer(customer_id)
                st.session_state["investigation"] = result
                st.session_state["investigation_customer"] = (
                    customer_id
                )
            except Exception as error:
                st.error(f"Investigation failed: {error}")

    result = st.session_state.get("investigation")

    if (
        result
        and st.session_state.get(
            "investigation_customer"
        ) == customer_id
    ):
        voice = result["voice_of_customer"]

        v1, v2, v3 = st.columns(3)
        v1.metric(
            "Sentiment",
            voice["sentiment"].title(),
        )
        v2.metric(
            "AI Risk",
            voice["risk_level"].title(),
        )
        v3.metric(
            "Confidence",
            f"{voice['confidence']:.0%}",
        )

        st.markdown(
            f"""
            <div class="ai-summary-card">
                <div class="finding-title">
                    Voice of Customer Summary
                </div>
                <div class="finding-summary">
                    {html.escape(voice["summary"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        signals = {
            "Competitor mentioned":
                voice["competitor_mentioned"],
            "Pricing objection":
                voice["pricing_objection"],
            "Product gap detected":
                voice["product_gap_detected"],
            "Churn language detected":
                voice["churn_language_detected"],
        }

        st.markdown("#### Signals detected")

        signal_columns = st.columns(4)

        for column, (label, detected) in zip(
            signal_columns,
            signals.items(),
        ):
            with column:
                if detected:
                    st.warning(f"⚠ {label}")
                else:
                    st.success(f"✓ {label}")

        st.markdown("#### Evidence")

        for evidence in voice["evidence"]:
            with st.expander(evidence["source_id"]):
                st.write(evidence["evidence_text"])
                st.caption(evidence["explanation"])

        st.markdown("### Recommended next actions")

        for index, action in enumerate(
            result["recommended_actions"],
            start=1,
        ):
            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-number">{index}</div>
                    <div>{html.escape(action)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Recent meeting notes")

    for note in get_recent_meeting_notes(
        customer_id,
        limit=5,
    ):
        with st.expander(
            f"{note.meeting_date} · {note.meeting_type}"
        ):
            st.write(note.note_text)


def sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                ⚡ SignalForge
            </div>
            <div class="sidebar-subtitle">
                Customer Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["Portfolio", "Investigation"],
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sidebar-divider"></div>',
            unsafe_allow_html=True,
        )

        st.caption("AI Agents")

        st.markdown(
            """
            <div class="agent-status">
                <span class="status-dot"></span>
                5 / 5 systems active
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page


def main() -> None:
    page = sidebar()

    if page == "Portfolio":
        render_portfolio()
    else:
        render_investigation()


if __name__ == "__main__":
    main()
