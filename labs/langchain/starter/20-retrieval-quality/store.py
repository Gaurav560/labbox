"""The rule book's pieces, embedded once and searched by meaning."""
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

MIN_SCORE = 0.3  # cosine similarity; chosen from real scores in this chapter


def build_store(chunks: list[Document]) -> InMemoryVectorStore:
    """Embeds every chunk with the gateway's embedding model and keeps vector, text and metadata together."""
    return InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model="ai-embed"))


def search(store: InMemoryVectorStore, question: str, k: int = 3, min_score: float = MIN_SCORE) -> list[tuple[Document, float]]:
    """The k closest chunks whose score is at least min_score, best first."""
    return [(doc, score) for doc, score in store.similarity_search_with_score(question, k=k) if score >= min_score]
