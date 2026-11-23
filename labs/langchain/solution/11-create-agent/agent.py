"""The same loop, built by LangChain: create_agent."""
from langchain.agents import create_agent

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM)


def tools_used(result: dict) -> list[str]:
    """The names of the tools the agent called, in order, from the messages of a finished run."""
    return [call["name"] for m in result["messages"] for call in getattr(m, "tool_calls", None) or []]
