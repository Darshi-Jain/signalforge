from __future__ import annotations

import argparse
import json

from src.workflows import investigate_customer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a complete SignalForge customer investigation."
    )
    parser.add_argument(
        "--customer",
        default="CUST-0001",
    )
    args = parser.parse_args()

    result = investigate_customer(args.customer)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
