"""The rule book, with chapter 20's fixes: split at sentences, and every chunk carries its document's title."""
from functools import cache
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

RULES = Path(__file__).with_name("rules")


@cache
def rule_store() -> InMemoryVectorStore:
    docs = [Document(p.read_text(), metadata={"source": p.name}) for p in sorted(RULES.glob("*.txt"))]
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30, separators=["\n\n", ". ", "\n", " ", ""],
                                              keep_separator="end")
    chunks = []
    for chunk in splitter.split_documents(docs):
        title = next(d for d in docs if d.metadata["source"] == chunk.metadata["source"]).page_content.splitlines()[0]
        text = chunk.page_content if chunk.page_content.startswith(title) else f"{title}: {chunk.page_content}"
        chunks.append(Document(text, metadata=chunk.metadata))
    return InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model="ai-embed"))
