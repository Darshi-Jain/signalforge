from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd


CSV_TABLES = {
    "customers.csv": "customers",
    "contracts.csv": "contracts",
    "usage_events.csv": "usage_events",
    "support_tickets.csv": "support_tickets",
    "stakeholders.csv": "stakeholders",
    "crm_activities.csv": "crm_activities",
}


def load_csv(
    connection: sqlite3.Connection,
    source_file: Path,
    table_name: str,
) -> int:
    dataframe = pd.read_csv(source_file)
    dataframe.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )
    return len(dataframe)


def load_meeting_notes(
    connection: sqlite3.Connection,
    source_file: Path,
) -> int:
    with source_file.open("r", encoding="utf-8") as file:
        records = json.load(file)

    dataframe = pd.DataFrame(records)
    dataframe.to_sql(
        "meeting_notes",
        connection,
        if_exists="replace",
        index=False,
    )
    return len(dataframe)


def create_indexes(connection: sqlite3.Connection) -> None:
    statements = [
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_customer_id
        ON customers(customer_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_contracts_customer_id
        ON contracts(customer_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_usage_customer_date
        ON usage_events(customer_id, period_date)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_support_customer_date
        ON support_tickets(customer_id, created_date)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_stakeholders_customer
        ON stakeholders(customer_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_crm_customer_date
        ON crm_activities(customer_id, activity_date)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_notes_customer_date
        ON meeting_notes(customer_id, meeting_date)
        """,
    ]

    for statement in statements:
        connection.execute(statement)

    connection.commit()


def validate_source_files(source_dir: Path) -> None:
    required_files = [
        *CSV_TABLES.keys(),
        "meeting_notes.json",
    ]

    missing = [
        filename
        for filename in required_files
        if not (source_dir / filename).exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing generated files: " + ", ".join(missing)
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load SignalForge synthetic data into SQLite."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/generated"),
        help="Directory containing generated CSV and JSON files.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("data/sqlite/signalforge.db"),
        help="Destination SQLite database.",
    )
    args = parser.parse_args()

    validate_source_files(args.source)
    args.database.parent.mkdir(parents=True, exist_ok=True)

    if args.database.exists():
        args.database.unlink()

    counts: dict[str, int] = {}

    with sqlite3.connect(args.database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        for filename, table_name in CSV_TABLES.items():
            counts[table_name] = load_csv(
                connection,
                args.source / filename,
                table_name,
            )

        counts["meeting_notes"] = load_meeting_notes(
            connection,
            args.source / "meeting_notes.json",
        )

        create_indexes(connection)

    print(f"Created database: {args.database}")
    for table_name, count in counts.items():
        print(f"{table_name}: {count} rows")


if __name__ == "__main__":
    main()
