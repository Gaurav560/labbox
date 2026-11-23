"""Navin as an MCP client: the tools come from the co-op's MCP server, started as a separate process."""
from pathlib import Path

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

SERVER = Path(__file__).with_name("coop_server.py")
SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


async def ask_over_mcp(question: str) -> tuple[list[str], str]:
    """Starts the server, lists its tools, and lets an agent use them. Returns (tool names, answer)."""
    async with MCPAdapter(SERVER) as adapter:
        tools = await adapter.list_tools()
        agent = create_agent("openai:ai-chat", tools=tools, system_prompt=SYSTEM)
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        return [t.name for t in tools], result["messages"][-1].content
