"""Facts that outlive a thread: a citizen's reply language, kept in a store and used in every new complaint."""
from dataclasses import dataclass
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

SYSTEM = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board, answering on WhatsApp. Reply in "
          "{language}, in at most two short sentences. Never promise a time: say a crew will be assigned.")
NOTE = "Read the citizen's message. If they ask Harsh to reply in a particular language, name it; otherwise null."


@dataclass
class Citizen:
    phone: str


class Prefs(BaseModel):
    language: Optional[str] = Field(None, description="the language the citizen asks for, or null")


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def note_preferences(state: MessagesState, runtime: Runtime[Citizen]) -> dict:
    prefs = model().with_structured_output(Prefs).invoke([SystemMessage(NOTE), state["messages"][-1]])
    # TODO (task save_preference): if prefs.language is set, save it for this citizen:
    #   runtime.store.put(("citizens", runtime.context.phone), "profile", {"language": prefs.language}).
    return {}


def respond(state: MessagesState, runtime: Runtime[Citizen]) -> dict:
    # TODO (task use_preference): read runtime.store.get(("citizens", runtime.context.phone), "profile"); if it
    #   exists, use item.value["language"] instead of English.
    language = "English"
    return {"messages": [model().invoke([SystemMessage(SYSTEM.format(language=language))] + state["messages"])]}


def build_graph(store=None):
    graph = StateGraph(MessagesState, context_schema=Citizen)
    graph.add_node("note_preferences", note_preferences)
    graph.add_node("respond", respond)
    graph.add_edge(START, "note_preferences")
    graph.add_edge("note_preferences", "respond")
    graph.add_edge("respond", END)
    return graph.compile(checkpointer=InMemorySaver(), store=store or InMemoryStore())
