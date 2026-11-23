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
    # TODO (task find_checkpoint): loop over app.get_state_history({"configurable": {"thread_id": thread}}) (newest
    #   first) and return the first snapshot whose .next == (node,). Return None if there is none.
    return None


def correct(app, thread: str, fields: dict) -> dict:
    """Replace what triage decided with `fields`, and run the rest of the graph again from there."""
    snapshot = snapshot_before(app, thread, "route")
    # TODO (task correct_and_rerun): write the fields into that checkpoint as if triage had returned them:
    #   config = app.update_state(snapshot.config, fields, as_node="triage"), then return app.invoke(None, config).
    return {}
