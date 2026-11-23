"""Navin, complete: tools, the rule book, memory per member, long-term facts, guardrails and the manager's approval."""
import re
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import (HumanInTheLoopMiddleware, ModelCallLimitMiddleware, ModelRequest, PIIMiddleware,
                                         ToolErrorMiddleware, dynamic_prompt)
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from booking import book_storage
from coop_tools import mandi_price, storage_cost
from knowledge import rule_store

SYSTEM = ("You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Before answering any question about storage, loans, spraying, membership or selling, always call "
          "search_rules with the member's whole question, and answer only from what it returns, naming the rule file in "
          "brackets. Only if it finds nothing, say you don't know and suggest calling the co-op office. When a member tells "
          "you a lasting fact about their farm, save it with remember. The manager approves every booking.")
AADHAAR = re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b")


@dataclass
class Member:
    member_id: str
    name: str


@tool
def search_rules(query: str) -> str:
    """Search the co-op's rule book (storage, loans, spraying, membership, selling) and return the matching rules.
    query: the member's whole question, in full, not a single keyword."""
    found = [(d, s) for d, s in rule_store().similarity_search_with_score(query, k=3) if s >= 0.3]
    if not found:
        return "No rule found for that question."
    return "\n\n".join(f"[{doc.metadata['source']}] {doc.page_content}" for doc, _ in found)


@tool
def remember(fact: str, runtime: ToolRuntime[Member]) -> str:
    """Save a lasting fact about the member's farm (crops, acres, village) for future conversations."""
    # TODO (task remember_fact): save the fact in the long-term store, under this member: the namespace is
    #   (runtime.context.member_id, "facts"); the key the next number (str(len(runtime.store.search(namespace)) + 1));
    #   the value {"fact": fact}. Use runtime.store.put(namespace, key, value), and return "Saved.".
    return "Not saved."


@dynamic_prompt
def member_prompt(request: ModelRequest) -> str:
    """The system prompt, with what Navin already knows about this member, from every earlier conversation."""
    member = request.runtime.context
    facts = [item.value["fact"] for item in request.runtime.store.search((member.member_id, "facts"))]
    known = " What you know about them: " + "; ".join(facts) + "." if facts else ""
    return f"{SYSTEM} You are talking to {member.name} ({member.member_id}).{known}"


def on_tool_error(error: Exception, request) -> str | None:
    if isinstance(error, ValueError):
        return f"{request.tool_call['name']} failed: {error}"
    return None


def find_aadhaar(text: str) -> list[dict]:
    return [{"type": "aadhaar", "value": m.group(), "start": m.start(), "end": m.end()} for m in AADHAAR.finditer(text)]


def navin_agent(store=None, checkpointer=None):
    return create_agent(
        "openai:ai-chat",
        tools=[search_rules, mandi_price, storage_cost, book_storage, remember],
        context_schema=Member,
        store=store or InMemoryStore(),
        checkpointer=checkpointer or InMemorySaver(),
        middleware=[
            PIIMiddleware("aadhaar", detector=find_aadhaar, strategy="mask", apply_to_input=True),
            member_prompt,
            ToolErrorMiddleware(on_tool_error),
            ModelCallLimitMiddleware(run_limit=8, exit_behavior="end"),
            HumanInTheLoopMiddleware(interrupt_on={"book_storage": {"allowed_decisions": ["approve", "edit", "reject"]}}),
        ],
    )
