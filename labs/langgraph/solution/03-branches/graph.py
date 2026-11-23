"""Branches and loops: each kind of complaint goes to its own team, and an unknown street is looked up again."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from rules import kind_of

# Street names as the water board's map spells them, and the spellings citizens use.
STREETS = {"gandhi chowk": "North", "station road": "South", "tilak nagar": "East", "old market": "Old Town"}
SPELLINGS = {"gandi chowk": "gandhi chowk", "stn road": "station road", "tilaknagar": "tilak nagar"}
MAX_TRIES = 2


class Ticket(TypedDict, total=False):
    text: str
    street: str
    kind: str
    zone: str
    tries: int
    team: str


def classify(state: Ticket) -> dict:
    return {"kind": kind_of(state["text"]), "tries": 0}


def find_zone(state: Ticket) -> dict:
    """One attempt: the street as written, then as corrected. Each attempt counts."""
    street = state["street"].lower().strip()
    if state["tries"] >= 1:
        street = SPELLINGS.get(street, street)
    return {"zone": STREETS.get(street, ""), "tries": state["tries"] + 1}


def after_find_zone(state: Ticket) -> str:
    if state["zone"]:
        return "route"
    if state["tries"] < MAX_TRIES:
        return "find_zone"
    return "ask_citizen"


def ask_citizen(state: Ticket) -> dict:
    return {"team": "front desk: please confirm the street name"}


def route(state: Ticket) -> dict:
    return {}


def choose_team(state: Ticket) -> str:
    """Which node handles this kind of complaint."""
    return {"dirty_water": "health_team", "billing": "billing_office"}.get(state["kind"], "repair_crew")


def health_team(state: Ticket) -> dict:
    return {"team": f"health team, {state['zone']} zone: water sample within 4 hours"}


def billing_office(state: Ticket) -> dict:
    return {"team": "billing office"}


def repair_crew(state: Ticket) -> dict:
    return {"team": f"repair crew, {state['zone']} zone"}


def build_graph():
    graph = StateGraph(Ticket)
    for name, fn in [("classify", classify), ("find_zone", find_zone), ("ask_citizen", ask_citizen), ("route", route),
                     ("health_team", health_team), ("billing_office", billing_office), ("repair_crew", repair_crew)]:
        graph.add_node(name, fn)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "find_zone")
    graph.add_conditional_edges("find_zone", after_find_zone, ["route", "find_zone", "ask_citizen"])
    graph.add_conditional_edges("route", choose_team, ["health_team", "billing_office", "repair_crew"])
    for end in ["ask_citizen", "health_team", "billing_office", "repair_crew"]:
        graph.add_edge(end, END)
    return graph.compile()
