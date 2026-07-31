from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class UsageRepository(BaseRepository):
    def get_customer_history(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM usage_events
            WHERE customer_id = ?
            ORDER BY period_date ASC, feature_name ASC
            """,
            (customer_id,),
        )

    def get_monthly_summary(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT
                period_date,
                ROUND(AVG(active_users), 2) AS active_users,
                MAX(purchased_seats) AS purchased_seats,
                ROUND(AVG(seat_utilization), 4) AS seat_utilization,
                ROUND(AVG(feature_adoption_rate), 4) AS feature_adoption_rate,
                SUM(api_calls) AS api_calls
            FROM usage_events
            WHERE customer_id = ?
            GROUP BY period_date
            ORDER BY period_date ASC
            """,
            (customer_id,),
        )
