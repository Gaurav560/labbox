"""A storm night: one triage per complaint, all at once (Send), and a node that chooses where to go next (Command)."""
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send

from rules import SEVERITY, kind_of

APPROVAL_OVER = 50_000  # rupees: bigger repairs need the engineer's approval
COST = {"leak": 18_000, "no_water": 65_000, "dirty_water": 40_000, "billing": 0, "other": 5_000}


class Night(TypedDict, total=False):
    complaints: list[str]
    tickets: Annotated[list[dict], operator.add]
    summary: str


class OneComplaint(TypedDict):
    text: str


def fan_out(state: Night) -> list[Send]:
    """One triage_one run per complaint, each with its own small state."""
    # TODO (task fan_out): return one Send("triage_one", {"text": text}) for every text in state["complaints"].
    return []


def triage_one(state: OneComplaint) -> dict:
    kind = kind_of(state["text"])
    return {"tickets": [{"text": state["text"], "kind": kind, "severity": SEVERITY[kind], "estimate": COST[kind]}]}


def summarise(state: Night) -> dict:
    urgent = sum(1 for t in state["tickets"] if t["severity"] == "urgent")
    return {"summary": f"{len(state['tickets'])} complaints, {urgent} urgent"}


def build_storm_graph():
    graph = StateGraph(Night)
    graph.add_node("triage_one", triage_one)
    graph.add_node("summarise", summarise)
    graph.add_conditional_edges(START, fan_out, ["triage_one"])
    graph.add_edge("triage_one", "summarise")
    graph.add_edge("summarise", END)
    return graph.compile()


class Repair(TypedDict, total=False):
    kind: str
    estimate: int
    status: str


def plan(state: Repair) -> Command[Literal["engineer_approval", "schedule"]]:
    """Decides the next step and updates the state in one return value."""
    # TODO (task command_goto): if state["estimate"] is over APPROVAL_OVER, return Command(goto="engineer_approval",
    #   update={"status": "waiting for the engineer"}); otherwise Command(goto="schedule", update={"status": "scheduled"}).
    return Command(goto="schedule", update={"status": "scheduled"})


def engineer_approval(state: Repair) -> dict:
    return {"status": state["status"] + " (sent to the executive engineer)"}


def schedule(state: Repair) -> dict:
    return {"status": state["status"] + " for tomorrow"}


def build_repair_graph():
    graph = StateGraph(Repair)
    graph.add_node("plan", plan)
    graph.add_node("engineer_approval", engineer_approval)
    graph.add_node("schedule", schedule)
    graph.add_edge(START, "plan")
    graph.add_edge("engineer_approval", END)
    graph.add_edge("schedule", END)
    return graph.compile()
