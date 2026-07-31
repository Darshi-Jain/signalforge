from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class SupportRepository(BaseRepository):
    def get_customer_tickets(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM support_tickets
            WHERE customer_id = ?
            ORDER BY created_date DESC
            """,
            (customer_id,),
        )

    def get_summary(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        return self.fetch_one(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(CASE WHEN severity = 'P1' THEN 1 ELSE 0 END)
                    AS critical_tickets,
                SUM(CASE WHEN reopened = 1 THEN 1 ELSE 0 END)
                    AS reopened_tickets,
                SUM(
                    CASE
                        WHEN status IN ('Open', 'Escalated')
                        THEN 1
                        ELSE 0
                    END
                ) AS unresolved_tickets,
                ROUND(AVG(resolution_hours), 2)
                    AS average_resolution_hours
            FROM support_tickets
            WHERE customer_id = ?
            """,
            (customer_id,),
        )
