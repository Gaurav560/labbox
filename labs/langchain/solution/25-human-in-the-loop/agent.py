"""A person approves before Navin books cold storage: the agent pauses, saves its state, and waits."""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from booking import book_storage
from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself. Book cold storage with book_storage when a member asks; the manager approves every booking."


def booking_agent():
    return create_agent(
        "openai:ai-chat",
        tools=[mandi_price, storage_cost, book_storage],
        system_prompt=SYSTEM,
        checkpointer=InMemorySaver(),
        middleware=[HumanInTheLoopMiddleware(interrupt_on={"book_storage": {"allowed_decisions": ["approve", "edit", "reject"]}})],
    )


def manager_decides(agent, thread_id: str, decision: dict):
    """Resumes a paused run with the manager's decision: approve, edit or reject."""
    return agent.invoke(Command(resume={"decisions": [decision]}), {"configurable": {"thread_id": thread_id}})
