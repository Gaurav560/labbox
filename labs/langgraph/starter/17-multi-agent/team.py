"""A supervisor and two specialists: the supervisor reads the case and hands it to billing or repairs, in turn."""
from typing import Literal

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from offices import BILLING_TOOLS, REPAIR_TOOLS

SUPERVISOR = ("You supervise the Ujjwal Nagar Water Board's desk. Read the citizen's message and the specialists' "
              "reports so far. Choose who acts next: billing (bills, meter readings), repairs (leaks, broken parts, "
              "visits), or FINISH when every problem the citizen raised has been handled by a specialist.")
BILLING = ("You are the billing office. Check the citizen's bills and meter readings with your tools, and hold a bill "
           "that looks wrong. Report what you found and did in two sentences. Handle only billing.")
REPAIRS = ("You are the repair office. Book a visit for any physical problem the citizen reports. Report what you did "
           "in one sentence. Handle only repairs.")
MAX_TURNS = 4


class Route(BaseModel):
    next: Literal["billing", "repairs", "FINISH"]
    reason: str


class Case(MessagesState):
    turns: int


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def supervisor(state: Case) -> Command[Literal["billing", "repairs", "__end__"]]:
    route = model().with_structured_output(Route).invoke([SystemMessage(SUPERVISOR)] + state["messages"])
    print(f"  supervisor -> {route.next}: {route.reason}", flush=True)
    # TODO (task supervisor_route): return Command(goto=END) when route.next is "FINISH" or MAX_TURNS turns were used;
    #   otherwise Command(goto=route.next, update={"turns": state.get("turns", 0) + 1}).
    return Command(goto=END)


def specialist(name: str, system: str, tools: list):
    agent = create_agent(model(), tools=tools, system_prompt=system)

    def node(state: Case) -> Command[Literal["supervisor"]]:
        result = agent.invoke({"messages": state["messages"]})
        report = AIMessage(result["messages"][-1].content, name=name)
        # TODO (task specialist_report): hand back to the supervisor with the report:
        #   Command(goto="supervisor", update={"messages": [report]}).
        return Command(goto="supervisor")
    return node


def build_graph():
    graph = StateGraph(Case)
    graph.add_node("supervisor", supervisor)
    graph.add_node("billing", specialist("billing", BILLING, BILLING_TOOLS))
    graph.add_node("repairs", specialist("repairs", REPAIRS, REPAIR_TOOLS))
    graph.add_edge(START, "supervisor")
    return graph.compile()
