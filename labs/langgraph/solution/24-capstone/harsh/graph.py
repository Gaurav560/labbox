"""Harsh, complete: intake, then the right part of the desk; big repairs wait for the engineer."""
from typing import Literal

from langchain.agents import create_agent
from langchain.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from harsh import prompts
from harsh.llm import model
from harsh.rules_search import search_rules
from harsh.tickets import TOOLS

APPROVAL_OVER = 50_000
REPAIR_COST = {"main_burst": 65_000, "valve": 18_000, "meter": 1_200}


class Intent(BaseModel):
    kind: Literal["status", "rules", "repair", "other"]
    problem: Literal["main_burst", "valve", "meter", "none"] = "none"
    street: str = Field("", description="the street named in the message, or empty")


class Desk(MessagesState):
    intent: dict
    approved: bool


def intake(state: Desk) -> dict:
    intent = model().with_structured_output(Intent).invoke([SystemMessage(prompts.INTAKE), state["messages"][-1]])
    return {"intent": intent.model_dump()}


def route_intent(state: Desk) -> str:
    return {"status": "status", "rules": "rules", "repair": "repair"}.get(state["intent"]["kind"], "other")


def repair(state: Desk) -> dict:
    cost = REPAIR_COST.get(state["intent"]["problem"], 0)
    if cost > APPROVAL_OVER:
        decision = interrupt({"problem": state["intent"]["problem"], "street": state["intent"]["street"], "estimate": cost,
                              "question": "Approve this repair?"})
        if not decision["approve"]:
            return {"approved": False, "messages": [AIMessage(
                f"The engineer could not approve this repair yet ({decision.get('note', '')}). A person will call you.")]}
    where = state["intent"]["street"] or "your street"
    return {"approved": True, "messages": [AIMessage(
        f"A crew is booked for the {state['intent']['problem'].replace('_', ' ')} at {where}: Thursday, 9:00 to 12:00.")]}


def other(state: Desk) -> dict:
    return {"messages": [AIMessage(prompts.OTHER)]}


def build_graph():
    graph = StateGraph(Desk)
    graph.add_node("intake", intake)
    graph.add_node("status", create_agent(model(), tools=TOOLS, system_prompt=prompts.STATUS))
    graph.add_node("rules", create_agent(model(), tools=[search_rules], system_prompt=prompts.RULES))
    graph.add_node("repair", repair)
    graph.add_node("other", other)
    graph.add_edge(START, "intake")
    graph.add_conditional_edges("intake", route_intent, ["status", "rules", "repair", "other"])
    for name in ["status", "rules", "repair", "other"]:
        graph.add_edge(name, END)
    return graph.compile()


graph = build_graph()
