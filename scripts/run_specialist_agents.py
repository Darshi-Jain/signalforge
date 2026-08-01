from __future__ import annotations

import argparse
import json

from src.agents import (
    CommercialRiskAgent,
    ProductAdoptionAgent,
    RelationshipIntelligenceAgent,
    SupportIntelligenceAgent,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run SignalForge deterministic specialist agents."
    )
    parser.add_argument(
        "--customer",
        default="CUST-0001",
    )
    args = parser.parse_args()

    agents = [
        ProductAdoptionAgent(),
        SupportIntelligenceAgent(),
        RelationshipIntelligenceAgent(),
        CommercialRiskAgent(),
    ]

    results = [
        agent.analyze(args.customer).model_dump()
        for agent in agents
    ]

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
