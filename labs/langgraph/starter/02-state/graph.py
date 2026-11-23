"""State that grows: a log every node adds to, and a severity that can only go up."""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from rules import SEVERITY, kind_of

ORDER = ["normal", "high", "urgent"]


def higher(current: str, new: str) -> str:
    """A reducer: of the severity already in the state and the new one, keep the more serious."""
    # TODO (task severity_reducer): if current is empty, return new. Otherwise return whichever of the two comes later
    #   in ORDER (normal < high < urgent): max(current, new, key=ORDER.index).
    return new


class Ticket(TypedDict, total=False):
    text: str
    kind: str
    severity: Annotated[str, higher]
    # TODO (task log_reducer): make log a list that grows: Annotated[list[str], operator.add]. As a plain list[str],
    #   each node's {"log": [...]} replaces the whole list.
    log: list[str]


def classify(state: Ticket) -> dict:
    kind = kind_of(state["text"])
    return {"kind": kind, "severity": SEVERITY[kind], "log": [f"classify: {kind}"]}


def check_location(state: Ticket) -> dict:
    """Complaints near a hospital or a school are never less than high."""
    text = state["text"].lower()
    if "hospital" in text or "school" in text:
        return {"severity": "high", "log": ["check_location: near a hospital or school"]}
    return {"log": ["check_location: nothing special"]}


def build_graph():
    graph = StateGraph(Ticket)
    graph.add_node("classify", classify)
    graph.add_node("check_location", check_location)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "check_location")
    graph.add_edge("check_location", END)
    return graph.compile()
