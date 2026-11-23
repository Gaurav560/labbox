"""Agentic RAG: Harsh decides when to search the rulebook, checks what it found, and rewrites a vague question."""
from functools import cache
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from rulebook import RULES

SYSTEM = ("You are Harsh, the complaint desk of the Ujjwal Nagar Water Board. For any question about the board's rules, "
          "charges or responsibilities, search the rulebook first. Reply in at most three short sentences.")
GRADE = ("Does the text below contain what is needed to answer the citizen's question? Answer relevant=true or false.")
REWRITE = ("Rewrite the citizen's question as a short search for the water board's rulebook, in the plain words a "
           "rulebook would use (for example 'roof tank' instead of 'the thing on my roof'). Return only the search.")
ANSWER = ("Answer the citizen's question using only the rulebook text below. If it does not say, say you will ask a "
          "person at the desk. At most three short sentences.\n\nRulebook:\n{context}")


class Grade(BaseModel):
    relevant: bool


class Chat(MessagesState):
    rewrites: int


def model():
    """The chat model, built when a node runs (so the checks can point it at their fake server)."""
    return init_chat_model("openai:ai-chat", temperature=0)


@cache
def rulebook() -> InMemoryVectorStore:
    return InMemoryVectorStore.from_texts(RULES, embedding=init_embeddings("openai:ai-embed"))


@tool
def search_rules(query: str) -> str:
    """Search the water board's rulebook. Returns the two most relevant sections."""
    return "\n\n".join(doc.page_content for doc in rulebook().similarity_search(query, k=2))


def question(state: Chat) -> str:
    """The citizen's question: the latest human message."""
    return [m for m in state["messages"] if m.type == "human"][-1].content


def search_or_answer(state: Chat) -> dict:
    return {"messages": [model().bind_tools([search_rules]).invoke([SystemMessage(SYSTEM)] + state["messages"])]}


def after_model(state: Chat) -> str:
    return "retrieve" if state["messages"][-1].tool_calls else END


def grade_documents(state: Chat) -> Literal["answer", "rewrite_question"]:
    """Is what the search found enough to answer? If not (and no rewrite was tried yet), rewrite the question."""
    found = state["messages"][-1].content
    # TODO (task grade_documents): ask model().with_structured_output(Grade) with [SystemMessage(GRADE),
    #   HumanMessage(f"Question: {question(state)}\n\nText:\n{found}")]. Return "answer" if it is relevant or a
    #   rewrite was already tried (state.get("rewrites", 0) >= 1); otherwise "rewrite_question".
    return "answer"


def rewrite_question(state: Chat) -> dict:
    # TODO (task rewrite_question): ask model() with [SystemMessage(REWRITE), HumanMessage(question(state))], and
    #   return {"messages": [HumanMessage(<its content>)], "rewrites": state.get("rewrites", 0) + 1}.
    return {"rewrites": state.get("rewrites", 0) + 1}


def answer(state: Chat) -> dict:
    found = state["messages"][-1].content
    original = [m for m in state["messages"] if m.type == "human"][0].content
    reply = model().invoke([SystemMessage(ANSWER.format(context=found)), HumanMessage(original)])
    return {"messages": [reply]}


def build_graph():
    graph = StateGraph(Chat)
    graph.add_node("search_or_answer", search_or_answer)
    graph.add_node("retrieve", ToolNode([search_rules]))
    graph.add_node("rewrite_question", rewrite_question)
    graph.add_node("answer", answer)
    graph.add_edge(START, "search_or_answer")
    graph.add_conditional_edges("search_or_answer", after_model, ["retrieve", END])
    graph.add_conditional_edges("retrieve", grade_documents, ["answer", "rewrite_question"])
    graph.add_edge("rewrite_question", "search_or_answer")
    graph.add_edge("answer", END)
    return graph.compile()
