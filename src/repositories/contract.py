from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class ContractRepository(BaseRepository):
    def get_by_customer(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        return self.fetch_one(
            """
            SELECT *
            FROM contracts
            WHERE customer_id = ?
            """,
            (customer_id,),
        )

    def list_upcoming_renewals(
        self,
        days: int = 120,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT
                c.customer_id,
                c.customer_name,
                c.segment,
                c.arr,
                ct.renewal_date,
                ct.renewal_days,
                ct.payment_status,
                ct.requested_seat_reduction_pct,
                ct.pricing_objection
            FROM customers c
            JOIN contracts ct
              ON c.customer_id = ct.customer_id
            WHERE ct.renewal_days <= ?
            ORDER BY ct.renewal_days ASC
            """,
            (days,),
        )
