"""Watching an agent work: its steps as they finish, and its answer as it is written."""
from langchain.agents import create_agent

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM)


def steps(agent, question: str, on_line=print) -> list[str]:
    """One line per finished step of the run, reported through on_line the moment it arrives."""
    lines = []
    for chunk in agent.stream({"messages": [{"role": "user", "content": question}]}, stream_mode="updates"):
        for step, update in chunk.items():
            for message in (update or {}).get("messages", []):
                calls = getattr(message, "tool_calls", None)
                new = [f"{step}: asks for {call['name']}" for call in calls] if calls else [f"{step}: {type(message).__name__}"]
                for line in new:
                    lines.append(line)
                    on_line(line)
    return lines


def answer_text(agent, question: str, on_piece) -> str:
    """The final answer, piece by piece, like chapter 8, but from an agent."""
    pieces = []
    for chunk, metadata in agent.stream({"messages": [{"role": "user", "content": question}]}, stream_mode="messages"):
        if metadata.get("langgraph_node") == "model" and isinstance(chunk.content, str) and chunk.content:
            on_piece(chunk.content)
            pieces.append(chunk.content)
    return "".join(pieces)
