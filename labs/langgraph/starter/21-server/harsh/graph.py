"""The graph the server runs. The server imports the module-level `graph` named in langgraph.json."""
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from harsh.prompts import SYSTEM
from harsh.tickets import TOOLS


def agent(state: MessagesState) -> dict:
    model = init_chat_model("openai:ai-chat", temperature=0).bind_tools(TOOLS)
    return {"messages": [model.invoke([SystemMessage(SYSTEM)] + state["messages"])]}


def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, ["tools", END])
    graph.add_edge("tools", "agent")
    # TODO (task server_graph): the server saves every thread itself, and refuses a graph with its own
    #   checkpointer. Compile without one: graph.compile() (and remove the InMemorySaver import).
    return graph.compile(checkpointer=InMemorySaver())


graph = build_graph()
