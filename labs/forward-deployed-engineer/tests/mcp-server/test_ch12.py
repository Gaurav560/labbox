import asyncio
import json

import r


async def session(fn):
    from mcp.client import Client
    import server
    async with Client(server.mcp) as client:
        return await fn(client)


def test_mcp_tools():
    def check():
        tools = asyncio.run(session(lambda c: c.list_tools())).tools
        names = sorted(t.name for t in tools)
        if names != ["get_policy", "in_force"]:
            return r.failed("mcp_tools", "Offer both functions as tools: put @mcp.tool() above get_policy and in_force.", ["get_policy", "in_force"], names)
        if any(len((t.description or "").strip()) < 20 for t in tools):
            return r.failed("mcp_tools", "Give each tool a docstring: it is the description every MCP client shows and every model reads.")

        async def calls(c):
            a = await c.call_tool("get_policy", {"policy_no": "DS-POL-40185"})
            b = await c.call_tool("in_force", {"policy_no": "DS-POL-40185", "on": "2026-10-04"})
            d = await c.call_tool("in_force", {"policy_no": "DS-POL-40925", "on": "2026-10-26"})
            return a, b, d
        a, b, d = asyncio.run(session(calls))
        if a.is_error or "MH12GH9012" not in a.content[0].text:
            return r.failed("mcp_tools", "get_policy over MCP should return the policy (vehicle MH12GH9012).", "the policy", a.content[0].text if a.content else a)
        if b.content[0].text.strip().lower() != "true" or d.content[0].text.strip().lower() != "false":
            return r.failed("mcp_tools", "in_force is True when start_date <= on <= end_date. DS-POL-40925 ended on 2026-10-20, so 26 October is outside.",
                            ("true", "false"), (b.content[0].text, d.content[0].text))
        r.passed("mcp_tools", "Two of Claimdesk's abilities, offered through one standard protocol: any MCP client can use them.")
    r.task("mcp_tools", check)


def test_tool_errors():
    def check():
        async def calls(c):
            return (await c.call_tool("get_policy", {"policy_no": "DS-POL-99999"}),
                    await c.call_tool("in_force", {"policy_no": "DS-POL-99999", "on": "2026-10-01"}))
        a, b = asyncio.run(session(calls))
        for name, res in (("get_policy", a), ("in_force", b)):
            text = res.content[0].text if res.content else ""
            if not res.is_error:
                return r.failed("tool_errors", f"{name} for an unknown policy answered as if it worked ({text!r}). Raise ToolError(f\"No policy {{policy_no}}\").",
                                "an error result", text)
            if "No policy DS-POL-99999" not in text:
                return r.failed("tool_errors", f"{name}'s error reached the client as {text!r}: a plain exception is hidden. Raise ToolError, whose message the client sees.",
                                "...No policy DS-POL-99999", text)
        r.passed("tool_errors", "The client learns exactly what was wrong; anything unexpected stays hidden instead of leaking your internals.")
    r.task("tool_errors", check)
