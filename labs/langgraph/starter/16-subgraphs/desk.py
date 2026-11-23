"""The desk graph, made of the offices' own graphs: billing shares its keys, repairs speaks its own language."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from billing import build_billing
from repairs import build_repairs
from rules import kind_of

REPAIRS = build_repairs()


class Ticket(TypedDict, total=False):
    ticket: str
    phone: str
    text: str
    kind: str
    verdict: str        # shared with the billing graph
    repair_log: list[str]


def triage(state: Ticket) -> dict:
    return {"kind": kind_of(state["text"])}


def to_office(state: Ticket) -> str:
    return {"billing": "billing", "leak": "repairs", "no_water": "repairs"}.get(state["kind"], END)


def repairs(state: Ticket) -> dict:
    """Translate a ticket into the repair office's language, run its graph, and translate the answer back."""
    # TODO (task map_state): invoke REPAIRS with {"job": state["ticket"]}, and return {"repair_log": result["log"]}.
    return {}


def build_graph():
    graph = StateGraph(Ticket)
    graph.add_node("triage", triage)
    # TODO (task add_subgraph): add the billing office's compiled graph itself as the node "billing":
    #   graph.add_node("billing", build_billing()). It shares the keys phone and verdict with Ticket.
    graph.add_node("billing", lambda state: {})
    graph.add_node("repairs", repairs)
    graph.add_edge(START, "triage")
    graph.add_conditional_edges("triage", to_office, ["billing", "repairs", END])
    graph.add_edge("billing", END)
    graph.add_edge("repairs", END)
    return graph.compile()
