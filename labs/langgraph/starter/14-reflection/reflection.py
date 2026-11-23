"""Reflection: before an answer is sent, a second model call checks every claim against the tool results."""
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from pydantic import BaseModel

from tickets import TOOLS

SYSTEM = ("You are Harsh, the friendly complaint desk of the Ujjwal Nagar Water Board, answering on WhatsApp. Use the "
          "ticket tools. Be warm and reassuring. Reply in at most three short sentences.")
CHECK = ("You check Harsh's answer before it is sent to a citizen. Split the answer into sentences and label each one: "
         "from_tools (every fact in it is in the tool results; the same day or time written differently counts, such "
         "as 18:00 and 6 pm), unknown (it says something is not known), courtesy (a greeting, thanks or offer of "
         "help), or new_claim (it says anything the tool results do not: a day such as 'tomorrow', a promise, a "
         "cause, or advice).")
MAX_ROUNDS = 2
HAND_OVER = "I have passed your question to a person at the desk, who will reply within the hour."


class Sentence(BaseModel):
    text: str
    kind: Literal["from_tools", "unknown", "courtesy", "new_claim"]


class Verdict(BaseModel):
    sentences: list[Sentence]


class Desk(MessagesState):
    rounds: int


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


def agent(state: Desk) -> dict:
    return {"messages": [model().bind_tools(TOOLS).invoke([SystemMessage(SYSTEM)] + state["messages"])]}


def after_agent(state: Desk) -> str:
    return "tools" if state["messages"][-1].tool_calls else "check_answer"


def check(answer: str, tool_results: str) -> list[str]:
    """The sentences of the answer that say more than the tool results: a model labels, Python decides."""
    # TODO (task check_claims): ask model().with_structured_output(Verdict) with [SystemMessage(CHECK),
    #   HumanMessage(f"Tool results:\n{tool_results}\n\nAnswer:\n{answer}")], then return the text of every
    #   sentence whose kind is "new_claim" (an empty list means the answer can be sent).
    return []


def check_answer(state: Desk) -> Command[Literal["agent", "hand_over", "__end__"]]:
    tool_results = "\n".join(m.content for m in state["messages"] if m.type == "tool") or "(no tools were used)"
    problems = check(state["messages"][-1].content, tool_results)
    rounds = state.get("rounds", 0) + 1
    feedback = ("Do not send that yet. These claims are not in the tool results: " + "; ".join(problems)
                + ". Rewrite the answer: keep every fact the tools gave, drop these claims, and say plainly what you "
                "do not know.")
    # TODO (task revise_or_finish): if there are no problems, return Command(goto=END). Otherwise, if rounds > MAX_ROUNDS,
    #   return Command(goto="hand_over"); else send the feedback back to the agent:
    #   Command(goto="agent", update={"messages": [HumanMessage(feedback, name="checker")], "rounds": rounds}).
    return Command(goto=END)


def hand_over(state: Desk) -> dict:
    return {"messages": [("ai", HAND_OVER)]}


def build_graph():
    graph = StateGraph(Desk)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("check_answer", check_answer)
    graph.add_node("hand_over", hand_over)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", after_agent, ["tools", "check_answer"])
    graph.add_edge("tools", "agent")
    graph.add_edge("hand_over", END)
    return graph.compile(checkpointer=InMemorySaver())
