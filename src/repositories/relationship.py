from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class RelationshipRepository(BaseRepository):
    def get_stakeholders(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM stakeholders
            WHERE customer_id = ?
            ORDER BY is_champion DESC, active DESC
            """,
            (customer_id,),
        )

    def get_crm_activities(
        self,
        customer_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM crm_activities
            WHERE customer_id = ?
            ORDER BY activity_date DESC
            LIMIT ?
            """,
            (customer_id, limit),
        )

    def get_summary(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        return self.fetch_one(
            """
            SELECT
                COUNT(*) AS stakeholder_count,
                SUM(CASE WHEN active = 1 THEN 1 ELSE 0 END)
                    AS active_stakeholders,
                SUM(
                    CASE
                        WHEN is_champion = 1 AND active = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS active_champions,
                SUM(
                    CASE
                        WHEN role = 'Executive Sponsor' AND active = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS active_executive_sponsors,
                MAX(last_engagement_date) AS latest_engagement_date
            FROM stakeholders
            WHERE customer_id = ?
            """,
            (customer_id,),
        )

    def get_no_response_count(
        self,
        customer_id: str,
    ) -> int:
        result = self.fetch_one(
            """
            SELECT COUNT(*) AS no_response_count
            FROM crm_activities
            WHERE customer_id = ?
              AND outcome = 'No response'
            """,
            (customer_id,),
        )

        return int(result["no_response_count"]) if result else 0
