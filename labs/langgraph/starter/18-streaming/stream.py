"""Streaming: progress events from Python nodes, and the reply token by token, so the citizen never stares at nothing."""
import time
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from tickets import TICKETS

REPLY = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board. Write the citizen a short update from the "
         "ticket facts below, one sentence per ticket. Use only these facts.")


class Ask(TypedDict, total=False):
    phone: str
    facts: str
    reply: str


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def lookup(state: Ask) -> dict:
    # TODO (task progress_events): write = get_stream_writer(), then write({"progress": "finding your tickets"}) here,
    #   and write({"progress": f"found {len(found)}, checking the crew schedule"}) after the tickets are found.
    found = [(tid, t) for tid, t in TICKETS.items() if t["phone"] == state["phone"]]
    time.sleep(0.5)  # the real ticket system is slow
    time.sleep(0.5)
    facts = "\n".join(f"{tid}: {t['kind']}, {t['status']}, {t['crew']}, {t['visit']}" for tid, t in found)
    return {"facts": facts}


def reply(state: Ask) -> dict:
    return {"reply": model().invoke([SystemMessage(REPLY), HumanMessage(state["facts"])]).content}


def build_graph():
    graph = StateGraph(Ask)
    graph.add_node("lookup", lookup)
    graph.add_node("reply", reply)
    graph.add_edge(START, "lookup")
    graph.add_edge("lookup", "reply")
    graph.add_edge("reply", END)
    return graph.compile()


def events(app, phone: str):
    """Yield ("progress", text) and ("token", text) as the run goes, for a chat screen to show at once."""
    # TODO (task stream_tokens): loop over app.stream({"phone": phone}, stream_mode=["custom", "messages"]), which
    #   gives (mode, chunk) pairs. For "custom", yield ("progress", chunk["progress"]). For "messages", chunk is
    #   (message, meta): yield ("token", message.content) when meta["langgraph_node"] == "reply" and there is content.
    yield "token", app.invoke({"phone": phone})["reply"]
