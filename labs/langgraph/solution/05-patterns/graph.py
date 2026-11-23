"""Two workflow patterns: parallel branches that join, and a writer checked by an evaluator in a loop."""
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

ZONES = {"gandhi chowk": "North", "station road": "South", "tilak nagar": "East", "old market": "Old Town"}
PAST_COMPLAINTS = {"station road": 6, "tilak nagar": 1}
MAX_DRAFTS = 3


# ----- Pattern 1: parallel branches -----

class Ticket(TypedDict, total=False):
    street: str
    zone: str
    past: int
    plan: str


def zone_lookup(state: Ticket) -> dict:
    return {"zone": ZONES.get(state["street"].lower(), "unknown")}


def history_lookup(state: Ticket) -> dict:
    return {"past": PAST_COMPLAINTS.get(state["street"].lower(), 0)}


def assign(state: Ticket) -> dict:
    """Runs once both lookups have finished: it needs the zone and the history."""
    extra = " and a survey of the old main (repeated complaints)" if state["past"] >= 5 else ""
    return {"plan": f"{state['zone']} zone crew{extra}"}


def build_parallel():
    graph = StateGraph(Ticket)
    graph.add_node("zone_lookup", zone_lookup)
    graph.add_node("history_lookup", history_lookup)
    graph.add_node("assign", assign)
    graph.add_edge(START, "zone_lookup")
    graph.add_edge(START, "history_lookup")
    graph.add_edge(["zone_lookup", "history_lookup"], "assign")
    graph.add_edge("assign", END)
    return graph.compile()


# ----- Pattern 2: evaluator and optimizer -----

WRITE = ("Write a public notice (at most 60 words) for the residents of Ujjwal Nagar about this planned water "
         "shutdown. If you are given feedback on an earlier draft, fix exactly what it says.")
GRADE = ("You check public notices for the Ujjwal Nagar Water Board. A good notice says: which area, the date, the start "
         "and end time, why, and to store water the day before. Is this notice good?")


class Grade(BaseModel):
    good: bool = Field(description="true only if every required item is present and correct")
    feedback: str = Field(description="what is missing or wrong, or an empty string")


class Notice(TypedDict, total=False):
    facts: str
    draft: str
    feedback: str
    good: bool
    drafts: int


def model():
    return init_chat_model("openai:ai-chat", temperature=0)


def write_notice(state: Notice) -> dict:
    ask = f"Facts: {state['facts']}" + (f"\nFeedback on your last draft: {state['feedback']}" if state.get("feedback") else "")
    draft = model().invoke([SystemMessage(WRITE), HumanMessage(ask)]).content
    return {"draft": draft, "drafts": state.get("drafts", 0) + 1}


def grade_notice(state: Notice) -> dict:
    grade = model().with_structured_output(Grade).invoke([SystemMessage(GRADE),
                                                          HumanMessage(f"Facts: {state['facts']}\nNotice: {state['draft']}")])
    return {"good": grade.good, "feedback": grade.feedback}


def next_step(state: Notice) -> str:
    """Done when the notice is good, or after MAX_DRAFTS drafts; otherwise write again with the feedback."""
    if state["good"] or state["drafts"] >= MAX_DRAFTS:
        return END
    return "write_notice"


def build_notice_loop():
    graph = StateGraph(Notice)
    graph.add_node("write_notice", write_notice)
    graph.add_node("grade_notice", grade_notice)
    graph.add_edge(START, "write_notice")
    graph.add_edge("write_notice", "grade_notice")
    graph.add_conditional_edges("grade_notice", next_step, ["write_notice", END])
    return graph.compile()
