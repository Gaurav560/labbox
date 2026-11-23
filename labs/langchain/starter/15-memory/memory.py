"""Navin remembers a conversation: a checkpointer saves every step, a thread id says which conversation."""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def memory_agent():
    # TODO (task memory_agent): like chapter 11's agent, plus checkpointer=InMemorySaver(), so every conversation's
    #   messages are saved between calls.
    return None


def ask(agent, member_id: str, text: str) -> str:
    # TODO (task thread_per_member): invoke the agent with the message and the config
    #   {"configurable": {"thread_id": member_id}}, so each member has their own conversation; return the last
    #   message's content.
    return ""
