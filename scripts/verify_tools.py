from __future__ import annotations

from src.tools import build_customer_context


def main() -> None:
    customer_id = "CUST-0001"
    context = build_customer_context(customer_id)

    print(context.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
