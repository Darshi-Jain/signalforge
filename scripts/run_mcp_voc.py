from __future__ import annotations

import argparse
import asyncio
import json

from agents import set_tracing_disabled

from src.agents.mcp_voc import investigate_voc_via_mcp


set_tracing_disabled(True)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer", default="CUST-0099")
    args = parser.parse_args()

    result = await investigate_voc_via_mcp(args.customer)

    print("\n=== MCP VOC FINDING ===")
    print(result["finding"].model_dump_json(indent=2))

    print("\n=== MCP VOC TRACE ===")
    for event in result["trace"]:
        print(json.dumps(event, indent=2))

    usage = result["usage"]

    print("\n=== USAGE ===")
    print(f"Requests: {usage.requests}")
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    print(f"Total tokens: {usage.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
