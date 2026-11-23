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
    # TODO (task first_graph): add the two nodes ("classify" and "write_reply", each with its function), then the
    #   edges START -> classify -> write_reply -> END, and return graph.compile().
    return graph


def steps(text: str) -> list[str]:
    """The names of the nodes that ran, in order, read from the graph's stream of updates."""
    # TODO (task trace_steps): loop over build_graph().stream({"text": text}, stream_mode="updates"). Each update is
    #   a dict {node name: what it returned}. Return the node names in the order they ran.
    return []
