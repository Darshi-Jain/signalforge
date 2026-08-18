from __future__ import annotations

from src.repositories import CustomerRepository
from src.tools import get_usage_trend


def compare_customer_usage_with_segment(
    customer_id: str,
) -> dict:
    customer_repo = CustomerRepository()
    customer = customer_repo.get_by_id(customer_id)

    if customer is None:
        raise ValueError(f"Unknown customer: {customer_id}")

    target = get_usage_trend(customer_id)

    peers = customer_repo.list_customers(limit=500)
    peer_values = []

    for peer in peers:
        if (
            peer["customer_id"] != customer_id
            and peer["segment"] == customer["segment"]
        ):
            try:
                peer_usage = get_usage_trend(peer["customer_id"])
                peer_values.append(
                    peer_usage.latest_seat_utilization
                )
            except ValueError:
                continue

    if not peer_values:
        return {
            "customer_id": customer_id,
            "segment": customer["segment"],
            "customer_seat_utilization":
                target.latest_seat_utilization,
            "segment_average": None,
            "difference": None,
        }

    segment_average = sum(peer_values) / len(peer_values)

    return {
        "customer_id": customer_id,
        "segment": customer["segment"],
        "customer_seat_utilization": round(
            target.latest_seat_utilization,
            4,
        ),
        "segment_average": round(segment_average, 4),
        "difference": round(
            target.latest_seat_utilization - segment_average,
            4,
        ),
    }
