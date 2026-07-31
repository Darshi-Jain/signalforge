from __future__ import annotations
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

class CustomerRepository:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.customers = pd.read_csv(data_dir / "customers.csv")
        self.usage = pd.read_csv(data_dir / "usage_metrics.csv")
        self.support = pd.read_csv(data_dir / "support_metrics.csv")
        self.engagement = pd.read_csv(data_dir / "engagement_metrics.csv")
        self.sentiment = pd.read_csv(data_dir / "sentiment_metrics.csv")

    def get_account(self, customer_id: str) -> dict:
        frames = [self.customers, self.usage, self.support, self.engagement, self.sentiment]
        merged = frames[0]
        for frame in frames[1:]:
            merged = merged.merge(frame, on="customer_id", how="left")
        row = merged.loc[merged.customer_id == customer_id]
        if row.empty:
            raise KeyError(f"Unknown customer_id: {customer_id}")
        return row.iloc[0].to_dict()

    def list_customers(self) -> list[str]:
        return self.customers.customer_id.tolist()
