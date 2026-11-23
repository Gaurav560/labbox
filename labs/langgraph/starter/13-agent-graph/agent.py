"""Harsh as an agent: a model that may call the ticket tools, in a loop you build yourself."""
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from tickets import TOOLS

SYSTEM = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board, answering on WhatsApp. Answer questions "
          "about complaints only from the ticket tools; never guess a status or a time. If you need the citizen's phone "
          "number, ask for it. Reply in at most three short sentences.")


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def agent(state: MessagesState) -> dict:
    """One model call: it answers, or asks for tools."""
    # TODO (task agent_node): give the model the tools with model().bind_tools(TOOLS) before invoking it, so it can
    #   ask for find_tickets and ticket_status.
    response = model().invoke([SystemMessage(SYSTEM)] + state["messages"])
    return {"messages": [response]}


def should_continue(state: MessagesState) -> str:
    """After the model: run the tools it asked for, or stop if it answered."""
    # TODO (task tool_loop): if the last message has tool_calls, return "tools" (ToolNode runs them, and the edge
    #   tools -> agent goes back to the model); otherwise return END.
    return END


def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", END])
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=InMemorySaver())
