"""Navin remembers a conversation: a checkpointer saves every step, a thread id says which conversation."""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def memory_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM,
                        checkpointer=InMemorySaver())


def ask(agent, member_id: str, text: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": text}]},
                          {"configurable": {"thread_id": member_id}})
    return result["messages"][-1].content
