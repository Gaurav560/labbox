"""Harsh's first graph: a complaint goes in, is classified, and gets a first reply."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from rules import HOURS, SEVERITY, kind_of


class Ticket(TypedDict, total=False):
    text: str
    kind: str
    reply: str


def classify(state: Ticket) -> dict:
    return {"kind": kind_of(state["text"])}


def write_reply(state: Ticket) -> dict:
    hours = HOURS[SEVERITY[state["kind"]]]
    return {"reply": f"Complaint received ({state['kind'].replace('_', ' ')}). We will respond within {hours} hours."}


def build_graph():
    graph = StateGraph(Ticket)
    graph.add_node("classify", classify)
    graph.add_node("write_reply", write_reply)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "write_reply")
    graph.add_edge("write_reply", END)
    return graph.compile()


def steps(text: str) -> list[str]:
    """The names of the nodes that ran, in order, read from the graph's stream of updates."""
    return [name for update in build_graph().stream({"text": text}, stream_mode="updates") for name in update]
