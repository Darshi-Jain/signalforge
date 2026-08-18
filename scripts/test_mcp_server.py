from __future__ import annotations

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp.server",
        ],
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            tools = await session.list_tools()

            print("\n=== MCP TOOLS DISCOVERED ===")

            for tool in tools.tools:
                print(f"- {tool.name}")

            print("\n=== MCP TOOL CALL ===")

            result = await session.call_tool(
                "get_customer_profile",
                {
                    "customer_id": "CUST-0099",
                },
            )

            for content in result.content:
                text = getattr(content, "text", None)

                if text:
                    print(text)


if __name__ == "__main__":
    asyncio.run(main())
