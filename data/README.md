# SignalForge Data

This project uses a synthetic enterprise Customer Success dataset.

The generated dataset is intentionally excluded from Git to keep the repository lightweight.

## Generate the dataset

python scripts/generate_enterprise_data.py \
  --customers 100 \
  --output data/generated

## Load into SQLite

python scripts/load_sqlite.py \
  --source data/generated \
  --database data/sqlite/signalforge.db

The generated CSV files and SQLite database are local development artifacts and are intentionally excluded from Git.
