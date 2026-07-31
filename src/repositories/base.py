from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class BaseRepository:
    """Shared SQLite access for SignalForge repositories."""

    def __init__(
        self,
        database_path: str | Path = "data/sqlite/signalforge.db",
    ) -> None:
        self.database_path = Path(database_path)

        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.database_path}. "
                "Run scripts/load_sqlite.py first."
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def fetch_one(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()

        return dict(row) if row else None

    def fetch_all(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()

        return [dict(row) for row in rows]
