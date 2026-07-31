from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class CustomerRepository(BaseRepository):
    def get_by_id(
        self,
        customer_id: str,
    ) -> dict[str, Any] | None:
        return self.fetch_one(
            """
            SELECT *
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,),
        )

    def list_customers(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM customers
            ORDER BY arr DESC
            LIMIT ?
            """,
            (limit,),
        )

    def list_by_risk_profile(
        self,
        risk_profile: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM customers
            WHERE risk_profile = ?
            ORDER BY arr DESC
            """,
            (risk_profile,),
        )
