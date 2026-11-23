from pathlib import Path

import r


def test_store_chunks(fake):
    def check():
        from loader import load_rules, split
        from store import build_store
        chunks = split(load_rules(Path("rules")))
        store = build_store(chunks)
        if len(store.store) != len(chunks):
            return r.failed("store_chunks", "The store is empty: return InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model=\"ai-embed\")).",
                            len(chunks), len(store.store))
        if not fake.embedding_requests or fake.embedding_requests[0].get("model") != "ai-embed":
            return r.failed("store_chunks", "Embed with OpenAIEmbeddings(model=\"ai-embed\"), the gateway's embedding model.")
        r.passed("store_chunks", f"{len(chunks)} chunks embedded in one batch and stored with their text and metadata.")
    r.task("store_chunks", check)


def test_search_threshold(fake):
    def check():
        from langchain_core.documents import Document
        from langchain_core.vectorstores import InMemoryVectorStore
        from langchain_openai import OpenAIEmbeddings
        from store import search
        store = InMemoryVectorStore.from_documents(
            [Document("onion storage crates", metadata={"source": "storage.txt"}), Document("crop loan per acre", metadata={"source": "loans.txt"}),
             Document("spray diary and fungicide", metadata={"source": "spraying.txt"})], OpenAIEmbeddings(model="ai-embed"))
        got = search(store, "onion storage", k=3, min_score=0.5)
        names = [d.metadata["source"] for d, _ in got]
        if names != ["storage.txt"]:
            return r.failed("search_threshold", "Keep only the (document, score) pairs whose score is at least min_score.", ["storage.txt"], names)
        if [d.metadata["source"] for d, _ in search(store, "onion storage", k=3, min_score=0.0)] != ["storage.txt", "loans.txt", "spraying.txt"][:3] and \
           len(search(store, "onion storage", k=3, min_score=0.0)) != 3:
            return r.failed("search_threshold", "With min_score 0 every one of the k results should be kept.")
        if search(store, "the capital of France", k=3, min_score=0.5):
            return r.failed("search_threshold", "A question unlike every chunk should return nothing above the threshold.")
        r.passed("search_threshold", "Closest is not close: a threshold turns \"the least bad match\" into \"no match\".")
    r.task("search_threshold", check)
