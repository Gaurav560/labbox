"""Harsh on WhatsApp: one thread per phone number, remembered by a checkpointer."""
import sqlite3

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph

SYSTEM = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board, answering on WhatsApp. Reply in at most "
          "two short sentences. Use what the citizen told you earlier in this chat. Never promise a time: say a crew "
          "will be assigned and an SMS will follow.")


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def respond(state: MessagesState) -> dict:
    return {"messages": [model().invoke([SystemMessage(SYSTEM)] + state["messages"])]}


def build_graph(checkpointer=None):
    graph = StateGraph(MessagesState)
    graph.add_node("respond", respond)
    graph.add_edge(START, "respond")
    graph.add_edge("respond", END)
    # TODO (task thread_memory): pass the checkpointer to compile(), so every step of every thread is saved.
    return graph.compile()


def ask(app, phone: str, text: str) -> str:
    """Send one WhatsApp message from this phone number, and return Harsh's answer."""
    # TODO (task thread_memory): make a config {"configurable": {"thread_id": phone}} and pass it to invoke as the
    #   second argument, so each phone number gets its own remembered thread.
    result = app.invoke({"messages": [HumanMessage(text)]})
    return result["messages"][-1].content


def open_saver(path: str) -> SqliteSaver:
    """A checkpointer that keeps every thread in a SQLite file, so chats survive a restart."""
    # TODO (task sqlite_saver): return SqliteSaver(sqlite3.connect(path, check_same_thread=False)).
    return None
