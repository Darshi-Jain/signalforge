from __future__ import annotations

import argparse

from src.agents import VoiceOfCustomerAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the SignalForge Voice of Customer Agent."
    )
    parser.add_argument(
        "--customer",
        default="CUST-0001",
        help="Customer ID to analyze.",
    )
    args = parser.parse_args()

    result = VoiceOfCustomerAgent().analyze(args.customer)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
