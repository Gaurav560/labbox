"""Long chats: send the model only recent messages, or fold old ones into a summary."""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, RemoveMessage, SystemMessage
from langchain_core.messages import trim_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

SYSTEM = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board, answering on WhatsApp. Reply in at most "
          "two short sentences. Use what the citizen told you earlier. If you do not know something, ask for it.")
SUMMARY = ("Summarise this WhatsApp complaint for the next person at the desk, in at most three sentences. Keep every "
           "fact: the citizen's name, full address, the problem, dates, and anything they asked for. "
           "The summary so far: {summary}")
KEEP = 4             # trimming: the model sees only the last 4 messages
SUMMARISE_OVER = 6   # summarising: when the chat has more than 6 messages, fold all but the last 2 into the summary


class Chat(MessagesState):
    summary: str


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def recent(messages: list) -> list:
    """The last KEEP messages, starting with a citizen's message (never with a reply cut from its question)."""
    # TODO (task trim_history): return trim_messages(messages, ...) with strategy="last", token_counter=len (count
    #   messages, not tokens), max_tokens=KEEP and start_on="human".
    return messages


def respond_trimmed(state: Chat) -> dict:
    return {"messages": [model().invoke([SystemMessage(SYSTEM)] + recent(state["messages"]))]}


def respond(state: Chat) -> dict:
    system = SYSTEM
    if state.get("summary"):
        system += f"\n\nEarlier in this chat (summary): {state['summary']}"
    return {"messages": [model().invoke([SystemMessage(system)] + state["messages"])]}


def needs_summary(state: Chat) -> str:
    return "summarise" if len(state["messages"]) > SUMMARISE_OVER else END


def summarise(state: Chat) -> dict:
    """Fold every message except the last two into the summary, and remove them from the state."""
    old = state["messages"][:-2]
    transcript = "\n".join(f"{m.type}: {m.content}" for m in old)
    prompt = SUMMARY.format(summary=state.get("summary") or "none yet")
    # TODO (task summarise_old): ask model() for the summary with [SystemMessage(prompt), HumanMessage(transcript)],
    #   then return {"summary": <its content>, "messages": [RemoveMessage(id=m.id) for m in old]}.
    return {}


def build_trimmed():
    graph = StateGraph(Chat)
    graph.add_node("respond", respond_trimmed)
    graph.add_edge(START, "respond")
    graph.add_edge("respond", END)
    return graph.compile(checkpointer=InMemorySaver())


def build_summarised():
    graph = StateGraph(Chat)
    graph.add_node("respond", respond)
    graph.add_node("summarise", summarise)
    graph.add_edge(START, "respond")
    graph.add_conditional_edges("respond", needs_summary, ["summarise", END])
    graph.add_edge("summarise", END)
    return graph.compile(checkpointer=InMemorySaver())
