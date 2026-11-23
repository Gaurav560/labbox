"""Every step is a checkpoint: read a complaint's history, correct a wrong step, and run on from there."""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from rules import HOURS, SEVERITY, kind_of

TEAMS = {"dirty_water": "health team", "billing": "billing office"}


class Ticket(TypedDict, total=False):
    text: str
    kind: str
    severity: str
    team: str
    reply: str


def triage(state: Ticket) -> dict:
    kind = kind_of(state["text"])
    return {"kind": kind, "severity": SEVERITY[kind]}


def route(state: Ticket) -> dict:
    return {"team": TEAMS.get(state["kind"], "repair crew")}


def reply(state: Ticket) -> dict:
    return {"reply": f"Your complaint is with the {state['team']}. We will respond within {HOURS[state['severity']]} hours."}


def build_graph():
    graph = StateGraph(Ticket)
    for name, node in [("triage", triage), ("route", route), ("reply", reply)]:
        graph.add_node(name, node)
    graph.add_edge(START, "triage")
    graph.add_edge("triage", "route")
    graph.add_edge("route", "reply")
    graph.add_edge("reply", END)
    return graph.compile(checkpointer=InMemorySaver())


def snapshot_before(app, thread: str, node: str):
    """The newest checkpoint of this thread at which `node` was about to run."""
    for snapshot in app.get_state_history({"configurable": {"thread_id": thread}}):
        if snapshot.next == (node,):
            return snapshot
    return None


def correct(app, thread: str, fields: dict) -> dict:
    """Replace what triage decided with `fields`, and run the rest of the graph again from there."""
    snapshot = snapshot_before(app, thread, "route")
    config = app.update_state(snapshot.config, fields, as_node="triage")
    return app.invoke(None, config)
