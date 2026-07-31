from __future__ import annotations

from typing import Any

from src.repositories.base import BaseRepository


class MeetingRepository(BaseRepository):
    def get_customer_notes(
        self,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM meeting_notes
            WHERE customer_id = ?
            ORDER BY meeting_date DESC
            """,
            (customer_id,),
        )

    def search_notes(
        self,
        customer_id: str,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        return self.fetch_all(
            """
            SELECT *
            FROM meeting_notes
            WHERE customer_id = ?
              AND LOWER(note_text) LIKE LOWER(?)
            ORDER BY meeting_date DESC
            LIMIT ?
            """,
            (customer_id, f"%{query}%", limit),
        )
