"""The rulebook as a search tool (chapter 15)."""
from functools import cache

from langchain.embeddings import init_embeddings
from langchain.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore

from harsh.rulebook import RULES


@cache
def rulebook() -> InMemoryVectorStore:
    return InMemoryVectorStore.from_texts(RULES, embedding=init_embeddings("openai:ai-embed"))


@tool
def search_rules(query: str) -> str:
    """Search the water board's rulebook. Returns the two most relevant sections."""
    return "\n\n".join(doc.page_content for doc in rulebook().similarity_search(query, k=2))
