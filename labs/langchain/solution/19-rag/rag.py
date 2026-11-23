"""Retrieval-augmented generation: Navin searches the rule book, then answers from what it found."""
from functools import cache
from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool

from coop_tools import mandi_price, storage_cost
from loader import load_rules, split
from store import build_store, search

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Before answering any question about storage, loans, spraying, membership or selling, always call search_rules first, and answer only from what it returns, naming the rule file in brackets, like [storage.txt]. Only if search_rules finds nothing, say you don't know and suggest calling the co-op office. Use your other tools for rates and charges."


@cache
def rule_store():
    """Built once, on first use: embedding the rule book costs a call, so do it once per process."""
    return build_store(split(load_rules(Path(__file__).with_name("rules"))))


@tool
def search_rules(query: str) -> str:
    """Search the co-op's rule book (storage, loans, spraying, membership, selling) and return the matching rules.
    query: the member's whole question, in full, not a single keyword."""
    found = search(rule_store(), query)
    if not found:
        return "No rule found for that question."
    return "\n\n".join(f"[{doc.metadata['source']}] {doc.page_content}" for doc, _ in found)


def rag_agent():
    return create_agent("openai:ai-chat", tools=[search_rules, mandi_price, storage_cost], system_prompt=SYSTEM)
