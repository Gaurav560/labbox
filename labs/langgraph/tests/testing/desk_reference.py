"""The desk graph under test: route each complaint, pause big repairs for the engineer, write the reply."""
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from rules import HOURS, SEVERITY, kind_of

APPROVAL_OVER = 50_000
TEAMS = {"dirty_water": "health team", "billing": "billing office"}
REPLY = "Write a two-sentence first reply to the citizen from these facts. Promise only the hours given."


class Ticket(TypedDict, total=False):
    text: str
    estimate: int
    kind: str
    team: str
    status: str
    reply: str


def triage(state: Ticket) -> dict:
    return {"kind": kind_of(state["text"])}


def route(state: Ticket) -> dict:
    return {"team": TEAMS.get(state["kind"], "repair crew")}


def needs_approval(state: Ticket) -> str:
    return "approval" if state.get("estimate", 0) > APPROVAL_OVER else "reply"


def approval(state: Ticket) -> dict:
    decision = interrupt({"estimate": state["estimate"], "question": "Approve this repair?"})
    return {"status": "approved" if decision["approve"] else f"refused: {decision.get('note', '')}"}


def after_approval(state: Ticket) -> str:
    return "reply" if state["status"] == "approved" else END


def build_graph(llm=None, checkpointer=None):
    """llm: the chat model for replies (tests pass a fake one). checkpointer: needed for approvals."""
    llm = llm or init_chat_model("openai:ai-chat", temperature=0)

    def reply(state: Ticket) -> dict:
        facts = f"Complaint: {state['text']}\nTeam: {state['team']}\nWithin {HOURS[SEVERITY[state['kind']]]} hours"
        return {"reply": llm.invoke([SystemMessage(REPLY), HumanMessage(facts)]).content}

    graph = StateGraph(Ticket)
    for name, node in [("triage", triage), ("route", route), ("approval", approval), ("reply", reply)]:
        graph.add_node(name, node)
    graph.add_edge(START, "triage")
    graph.add_edge("triage", "route")
    graph.add_conditional_edges("route", needs_approval, ["approval", "reply"])
    graph.add_conditional_edges("approval", after_approval, ["reply", END])
    graph.add_edge("reply", END)
    return graph.compile(checkpointer=checkpointer)
