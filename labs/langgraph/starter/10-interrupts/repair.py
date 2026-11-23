"""Big repairs wait for the executive engineer: the graph pauses, and resumes with her decision."""
import sqlite3
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

APPROVAL_OVER = 50_000
BRIEF = ("Write a brief for the executive engineer of the Ujjwal Nagar Water Board, who must approve or refuse a "
         "repair. Two sentences: what the work is and where, and why it is needed now. Plain words, no greeting.")


class Repair(TypedDict, total=False):
    job: str
    work: str
    street: str
    estimate: int
    brief: str
    approved: bool
    note: str
    status: str


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def write_brief(state: Repair) -> dict:
    facts = f"Work: {state['work']}\nStreet: {state['street']}\nEstimate: Rs {state['estimate']:,}"
    return {"brief": model().invoke([SystemMessage(BRIEF), HumanMessage(facts)]).content}


def needs_approval(state: Repair) -> str:
    return "approval" if state["estimate"] > APPROVAL_OVER else "schedule"


def approval(state: Repair) -> dict:
    print("  (the approval node starts)", flush=True)
    # TODO (task pause_for_engineer): call interrupt({...}) with the job, the estimate, the brief and
    #   "question": "Approve this repair?". It pauses the graph; when the engineer answers, interrupt returns her
    #   answer, a dict like {"approve": True, "note": "..."}. Return {"approved": ..., "note": ...} from it.
    return {"approved": True, "note": ""}


def after_approval(state: Repair) -> str:
    return "schedule" if state["approved"] else "refuse"


def schedule(state: Repair) -> dict:
    return {"status": "scheduled" + (f" ({state['note']})" if state.get("note") else "")}


def refuse(state: Repair) -> dict:
    return {"status": f"refused: {state['note']}"}


def build_graph(checkpointer):
    graph = StateGraph(Repair)
    for name, node in [("write_brief", write_brief), ("approval", approval), ("schedule", schedule), ("refuse", refuse)]:
        graph.add_node(name, node)
    graph.add_edge(START, "write_brief")
    graph.add_conditional_edges("write_brief", needs_approval, ["approval", "schedule"])
    graph.add_conditional_edges("approval", after_approval, ["schedule", "refuse"])
    graph.add_edge("schedule", END)
    graph.add_edge("refuse", END)
    return graph.compile(checkpointer=checkpointer)


def decide(app, job: str, approve: bool, note: str = "") -> dict:
    """The engineer's answer: resume the paused job with it."""
    # TODO (task resume_with_decision): invoke the app with Command(resume={"approve": approve, "note": note}) and
    #   the job's config {"configurable": {"thread_id": job}}, and return the result.
    return {}


def open_saver(path: str = "repairs.db") -> SqliteSaver:
    return SqliteSaver(sqlite3.connect(path, check_same_thread=False))
