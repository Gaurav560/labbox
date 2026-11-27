"""Starts server.py the way an MCP client does (as a separate process, talking over stdin and stdout), lists its
tools, and calls them. Run it with: python try_server.py"""
import asyncio

from mcp import StdioServerParameters
from mcp.client import Client


async def main():
    async with Client(StdioServerParameters(command="python", args=["server.py"])) as client:
        for tool in (await client.list_tools()).tools:
            print(f"tool {tool.name}: {tool.description.splitlines()[0]}")
        for name, args in [("get_policy", {"policy_no": "DS-POL-40185"}),
                           ("in_force", {"policy_no": "DS-POL-40185", "on": "2026-10-04"}),
                           ("in_force", {"policy_no": "DS-POL-40925", "on": "2026-10-26"}),
                           ("get_policy", {"policy_no": "DS-POL-99999"})]:
            result = await client.call_tool(name, args)
            text = result.content[0].text if result.content else ""
            print(f"{name} {args} -> error={result.is_error} {text}")


asyncio.run(main())
