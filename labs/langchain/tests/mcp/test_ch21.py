import asyncio
import json

import r
from fake_openai import Reply


def test_mcp_server():
    def check():
        from coop_server import mcp
        tools = asyncio.run(mcp.list_tools())
        names = sorted(t.name for t in tools)
        if names != ["mandi_price", "storage_cost"]:
            return r.failed("mcp_server", "Offer both functions as tools: put @mcp.tool above each def.", "['mandi_price', 'storage_cost']", names)
        from fastmcp import Client

        async def call():
            async with Client(mcp) as client:
                return await client.call_tool("storage_cost", {"crates": 15, "days": 4})
        result = asyncio.run(call())
        if "120" not in json.dumps(result.content[0].model_dump()):
            return r.failed("mcp_server", "storage_cost over MCP should return 15 x 4 x 2 = 120.")
        r.passed("mcp_server", "The co-op's tools as an MCP server: any MCP client, in any language, can now use them.")
    r.task("mcp_server", check)


def test_mcp_agent(fake):
    def check():
        from client import ask_over_mcp
        fake.script = lambda b: Reply.tool("storage_cost", {"crates": 15, "days": 4}) if len(fake.chat_requests) == 1 else Reply("Rs 120.")
        names, answer = asyncio.run(ask_over_mcp("15 crates for 4 days?"))
        if sorted(names) != ["mandi_price", "storage_cost"]:
            return r.failed("mcp_agent", "List the server's tools with await adapter.list_tools(), inside async with MCPAdapter(SERVER).",
                            "['mandi_price', 'storage_cost']", names)
        results = [m["content"] for m in fake.chat_requests[-1]["messages"] if m["role"] == "tool"]
        if not results or "120" not in json.dumps(results):
            return r.failed("mcp_agent", "The agent should call storage_cost on the server and send its result back to the model.")
        if answer != "Rs 120.":
            return r.failed("mcp_agent", "Return the last message's content as the answer.", "Rs 120.", answer)
        r.passed("mcp_agent", "Navin used tools from a separate process it had never seen, through one protocol.")
    r.task("mcp_agent", check)
