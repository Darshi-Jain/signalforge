from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd


RANDOM_SEED = 42

INDUSTRIES = [
    "Financial Services",
    "Healthcare",
    "Retail",
    "Technology",
    "Manufacturing",
    "Media",
    "Logistics",
    "Education",
]

SEGMENTS = ["Mid-Market", "Enterprise", "Strategic"]

FEATURES = [
    "Analytics",
    "Workflow Automation",
    "API Integration",
    "Executive Reporting",
    "Collaboration",
]

SUPPORT_TOPICS = [
    "API authentication",
    "reporting latency",
    "user provisioning",
    "data export",
    "workflow configuration",
    "billing question",
    "dashboard permissions",
]

MEETING_TYPES = [
    "Onboarding",
    "Monthly Success Review",
    "Quarterly Business Review",
    "Technical Review",
    "Renewal Planning",
]

RISK_PROFILES = [
    "healthy",
    "usage_decline",
    "support_escalation",
    "champion_departure",
    "commercial_risk",
    "competitor_risk",
    "seasonal_decline",
]


def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, max(days, 0)))


def customer_id(index: int) -> str:
    return f"CUST-{index:04d}"


def generate_customers(count: int, today: date) -> pd.DataFrame:
    rows: list[dict] = []

    for index in range(1, count + 1):
        segment = random.choices(
            SEGMENTS,
            weights=[0.45, 0.40, 0.15],
            k=1,
        )[0]

        arr_ranges = {
            "Mid-Market": (25_000, 100_000),
            "Enterprise": (100_000, 350_000),
            "Strategic": (350_000, 900_000),
        }

        arr_min, arr_max = arr_ranges[segment]
        risk_profile = random.choices(
            RISK_PROFILES,
            weights=[0.42, 0.13, 0.10, 0.09, 0.09, 0.09, 0.08],
            k=1,
        )[0]

        start_date = random_date(
            today - timedelta(days=1_500),
            today - timedelta(days=120),
        )

        rows.append(
            {
                "customer_id": customer_id(index),
                "customer_name": f"Customer {index:03d}",
                "industry": random.choice(INDUSTRIES),
                "segment": segment,
                "arr": round(random.uniform(arr_min, arr_max), 2),
                "contract_start_date": start_date.isoformat(),
                "account_owner": f"CSM {random.randint(1, 12):02d}",
                "lifecycle_stage": random.choice(
                    ["Adoption", "Growth", "Renewal", "Mature"]
                ),
                "risk_profile": risk_profile,
                "known_churn_outcome": risk_profile
                in {
                    "usage_decline",
                    "support_escalation",
                    "commercial_risk",
                    "competitor_risk",
                },
            }
        )

    return pd.DataFrame(rows)


def generate_contracts(
    customers: pd.DataFrame,
    today: date,
) -> pd.DataFrame:
    rows: list[dict] = []

    for customer in customers.to_dict("records"):
        risk = customer["risk_profile"]
        renewal_days = random.randint(30, 365)

        if risk in {"commercial_risk", "competitor_risk"}:
            renewal_days = random.randint(25, 100)

        rows.append(
            {
                "customer_id": customer["customer_id"],
                "renewal_date": (
                    today + timedelta(days=renewal_days)
                ).isoformat(),
                "renewal_days": renewal_days,
                "contract_term_months": random.choice([12, 24, 36]),
                "payment_status": (
                    "Delayed"
                    if risk == "commercial_risk"
                    else random.choice(["Current", "Current", "Current", "Due Soon"])
                ),
                "requested_seat_reduction_pct": (
                    random.choice([10, 15, 20, 25])
                    if risk == "commercial_risk"
                    else 0
                ),
                "pricing_objection": risk
                in {"commercial_risk", "competitor_risk"},
            }
        )

    return pd.DataFrame(rows)


def generate_usage(
    customers: pd.DataFrame,
    today: date,
    months: int = 12,
) -> pd.DataFrame:
    rows: list[dict] = []

    for customer in customers.to_dict("records"):
        risk = customer["risk_profile"]
        base_users = random.randint(40, 600)
        purchased_seats = int(base_users * random.uniform(1.2, 1.8))

        for month_offset in range(months):
            period_date = today - timedelta(days=30 * (months - month_offset - 1))
            trend_factor = 1.0

            if risk == "usage_decline" and month_offset >= months - 4:
                trend_factor = 1.0 - (month_offset - (months - 5)) * 0.11

            if risk == "seasonal_decline" and month_offset >= months - 2:
                trend_factor = 0.58

            if risk == "healthy":
                trend_factor = 1.0 + month_offset * 0.01

            active_users = max(
                5,
                int(base_users * trend_factor * random.uniform(0.92, 1.08)),
            )

            seat_utilization = min(active_users / purchased_seats, 1.0)

            for feature in FEATURES:
                feature_factor = random.uniform(0.35, 0.90)

                if risk == "usage_decline" and month_offset >= months - 4:
                    feature_factor *= trend_factor

                rows.append(
                    {
                        "customer_id": customer["customer_id"],
                        "period_date": period_date.isoformat(),
                        "feature_name": feature,
                        "active_users": active_users,
                        "purchased_seats": purchased_seats,
                        "seat_utilization": round(seat_utilization, 4),
                        "feature_adoption_rate": round(feature_factor, 4),
                        "api_calls": max(
                            0,
                            int(
                                active_users
                                * random.randint(10, 100)
                                * trend_factor
                            ),
                        ),
                    }
                )

    return pd.DataFrame(rows)


def generate_support_tickets(
    customers: pd.DataFrame,
    today: date,
) -> pd.DataFrame:
    rows: list[dict] = []
    ticket_number = 1

    for customer in customers.to_dict("records"):
        risk = customer["risk_profile"]
        ticket_count = random.randint(1, 8)

        if risk == "support_escalation":
            ticket_count = random.randint(9, 16)

        for _ in range(ticket_count):
            created_date = random_date(
                today - timedelta(days=180),
                today,
            )

            severity = random.choice(["P3", "P3", "P2", "P2", "P1"])

            if risk == "support_escalation":
                severity = random.choice(["P2", "P1", "P1"])

            reopened = risk == "support_escalation" and random.random() < 0.45
            status = random.choice(["Resolved", "Resolved", "Open"])

            if risk == "support_escalation":
                status = random.choice(["Open", "Escalated", "Resolved"])

            topic = random.choice(SUPPORT_TOPICS)

            rows.append(
                {
                    "ticket_id": f"TICK-{ticket_number:05d}",
                    "customer_id": customer["customer_id"],
                    "created_date": created_date.isoformat(),
                    "severity": severity,
                    "status": status,
                    "topic": topic,
                    "reopened": reopened,
                    "resolution_hours": round(
                        random.uniform(
                            2,
                            16 if risk != "support_escalation" else 72,
                        ),
                        2,
                    ),
                    "ticket_text": (
                        f"Customer reported an issue involving {topic}. "
                        f"Current status is {status}."
                    ),
                }
            )
            ticket_number += 1

    return pd.DataFrame(rows)


def generate_stakeholders(
    customers: pd.DataFrame,
    today: date,
) -> pd.DataFrame:
    rows: list[dict] = []

    for customer in customers.to_dict("records"):
        risk = customer["risk_profile"]
        stakeholder_count = random.randint(2, 5)

        for stakeholder_index in range(1, stakeholder_count + 1):
            is_champion = stakeholder_index == 1
            active = True

            if risk == "champion_departure" and is_champion:
                active = False

            rows.append(
                {
                    "stakeholder_id": (
                        f"{customer['customer_id']}-STK-{stakeholder_index:02d}"
                    ),
                    "customer_id": customer["customer_id"],
                    "name": f"Stakeholder {stakeholder_index}",
                    "role": random.choice(
                        [
                            "Executive Sponsor",
                            "Business Champion",
                            "Technical Lead",
                            "Procurement",
                            "Operations Manager",
                        ]
                    ),
                    "is_champion": is_champion,
                    "active": active,
                    "last_engagement_date": (
                        today
                        - timedelta(
                            days=(
                                random.randint(70, 150)
                                if risk == "champion_departure"
                                else random.randint(3, 45)
                            )
                        )
                    ).isoformat(),
                }
            )

    return pd.DataFrame(rows)


def generate_crm_activities(
    customers: pd.DataFrame,
    today: date,
) -> pd.DataFrame:
    rows: list[dict] = []
    activity_number = 1

    for customer in customers.to_dict("records"):
        risk = customer["risk_profile"]
        count = random.randint(4, 12)

        for _ in range(count):
            activity_date = random_date(
                today - timedelta(days=180),
                today,
            )

            rows.append(
                {
                    "activity_id": f"ACT-{activity_number:05d}",
                    "customer_id": customer["customer_id"],
                    "activity_date": activity_date.isoformat(),
                    "activity_type": random.choice(
                        [
                            "Email",
                            "Call",
                            "Executive Meeting",
                            "CSM Follow-up",
                            "Renewal Review",
                        ]
                    ),
                    "outcome": (
                        "No response"
                        if risk
                        in {
                            "champion_departure",
                            "competitor_risk",
                        }
                        and random.random() < 0.45
                        else random.choice(
                            [
                                "Completed",
                                "Follow-up required",
                                "Positive engagement",
                            ]
                        )
                    ),
                }
            )
            activity_number += 1

    return pd.DataFrame(rows)


def meeting_note_for_risk(risk: str) -> str:
    notes = {
        "healthy": (
            "The customer confirmed strong adoption and positive business "
            "outcomes. The executive sponsor supports expansion discussions."
        ),
        "usage_decline": (
            "The customer shared that several teams have stopped using core "
            "workflows. Additional enablement may be required."
        ),
        "support_escalation": (
            "The customer expressed frustration with recurring technical "
            "issues and requested a formal root-cause review."
        ),
        "champion_departure": (
            "The primary champion recently left the organization. A new "
            "business owner has not yet been confirmed."
        ),
        "commercial_risk": (
            "The customer raised pricing concerns and requested a reduction "
            "in licensed seats before renewal."
        ),
        "competitor_risk": (
            "The customer stated that they are evaluating a competing "
            "platform with stronger reporting capabilities."
        ),
        "seasonal_decline": (
            "Usage has declined due to the customer's documented seasonal "
            "shutdown. Activity is expected to recover next quarter."
        ),
    }
    return notes[risk]


def generate_meeting_notes(
    customers: pd.DataFrame,
    today: date,
) -> list[dict]:
    rows: list[dict] = []
    note_number = 1

    for customer in customers.to_dict("records"):
        count = random.randint(2, 6)

        for index in range(count):
            meeting_date = random_date(
                today - timedelta(days=180),
                today,
            )

            note = meeting_note_for_risk(customer["risk_profile"])

            if index > 0 and random.random() < 0.55:
                note = (
                    "Reviewed current objectives, adoption progress, open "
                    "actions, and next steps with the customer team."
                )

            rows.append(
                {
                    "note_id": f"NOTE-{note_number:05d}",
                    "customer_id": customer["customer_id"],
                    "meeting_date": meeting_date.isoformat(),
                    "meeting_type": random.choice(MEETING_TYPES),
                    "attendees": random.randint(2, 8),
                    "note_text": note,
                }
            )
            note_number += 1

    return rows


def write_outputs(
    output_dir: Path,
    customers: pd.DataFrame,
    contracts: pd.DataFrame,
    usage: pd.DataFrame,
    support: pd.DataFrame,
    stakeholders: pd.DataFrame,
    crm: pd.DataFrame,
    meeting_notes: list[dict],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    customers.to_csv(output_dir / "customers.csv", index=False)
    contracts.to_csv(output_dir / "contracts.csv", index=False)
    usage.to_csv(output_dir / "usage_events.csv", index=False)
    support.to_csv(output_dir / "support_tickets.csv", index=False)
    stakeholders.to_csv(output_dir / "stakeholders.csv", index=False)
    crm.to_csv(output_dir / "crm_activities.csv", index=False)

    with (output_dir / "meeting_notes.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(meeting_notes, file, indent=2)

    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "customer_count": len(customers),
        "contract_count": len(contracts),
        "usage_record_count": len(usage),
        "support_ticket_count": len(support),
        "stakeholder_count": len(stakeholders),
        "crm_activity_count": len(crm),
        "meeting_note_count": len(meeting_notes),
    }

    with (output_dir / "dataset_summary.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summary, file, indent=2)

    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic enterprise Customer Success data."
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=100,
        help="Number of customer accounts to generate.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/generated"),
        help="Output directory.",
    )
    args = parser.parse_args()

    random.seed(RANDOM_SEED)
    today = date.today()

    customers = generate_customers(args.customers, today)
    contracts = generate_contracts(customers, today)
    usage = generate_usage(customers, today)
    support = generate_support_tickets(customers, today)
    stakeholders = generate_stakeholders(customers, today)
    crm = generate_crm_activities(customers, today)
    meeting_notes = generate_meeting_notes(customers, today)

    write_outputs(
        output_dir=args.output,
        customers=customers,
        contracts=contracts,
        usage=usage,
        support=support,
        stakeholders=stakeholders,
        crm=crm,
        meeting_notes=meeting_notes,
    )


if __name__ == "__main__":
    main()
