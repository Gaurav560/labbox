"""Watching an agent work: its steps as they finish, and its answer as it is written."""
from langchain.agents import create_agent

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM)


def steps(agent, question: str, on_line=print) -> list[str]:
    """One line per finished step of the run, reported through on_line the moment it arrives."""
    lines = []
    # TODO (task stream_steps): loop over agent.stream({"messages": [...]}, stream_mode="updates"). Each chunk is a
    #   dict {step name: {"messages": [new messages]}}. For each new message: if it has tool_calls, add
    #   f"{step}: asks for {name}" for each call; otherwise add f"{step}: {type(message).__name__}". Call on_line(line)
    #   for each line as soon as you add it.
    return lines


def answer_text(agent, question: str, on_piece) -> str:
    """The final answer, piece by piece, like chapter 8, but from an agent."""
    pieces = []
    # TODO (task stream_answer_text): loop over agent.stream({...}, stream_mode="messages"), which yields
    #   (message_chunk, metadata) pairs. Keep only chunks from the "model" step (metadata["langgraph_node"]) that
    #   have text content; call on_piece(text) for each, and return them joined.
    return "".join(pieces)
