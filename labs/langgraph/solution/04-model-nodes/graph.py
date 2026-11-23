"""A model in a node: the complaint is read by a model, and the first reply written by one."""
from typing import Literal, TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

HOURS = {"urgent": 4, "high": 24, "normal": 72}
TRIAGE = ("You triage complaints for the Ujjwal Nagar Water Board. dirty_water (any colour, smell or taste problem) is "
          "always urgent; no_water and leak are high; billing and other are normal.")
REPLY = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board. Write a short, kind first reply to the "
         "citizen: two sentences at most. Promise only the response time you are given, nothing else.")


class Triage(BaseModel):
    """What the complaint is about, how serious it is, and where."""
    kind: Literal["dirty_water", "no_water", "leak", "billing", "other"]
    severity: Literal["urgent", "high", "normal"]
    street: str = Field(description="the street or area named in the complaint, or an empty string")


class Ticket(TypedDict, total=False):
    text: str
    kind: str
    severity: str
    street: str
    reply: str


def model():
    return init_chat_model("openai:ai-chat", temperature=0)


def triage(state: Ticket) -> dict:
    result = model().with_structured_output(Triage).invoke([SystemMessage(TRIAGE), HumanMessage(state["text"])])
    return result.model_dump()


def draft_reply(state: Ticket) -> dict:
    facts = (f"Complaint: {state['text']}\nKind: {state['kind']}\nStreet: {state['street'] or 'not given'}\n"
             f"Response time: within {HOURS[state['severity']]} hours")
    return {"reply": model().invoke([SystemMessage(REPLY), HumanMessage(facts)]).content}


def build_graph():
    graph = StateGraph(Ticket)
    graph.add_node("triage", triage)
    graph.add_node("draft_reply", draft_reply)
    graph.add_edge(START, "triage")
    graph.add_edge("triage", "draft_reply")
    graph.add_edge("draft_reply", END)
    return graph.compile()
