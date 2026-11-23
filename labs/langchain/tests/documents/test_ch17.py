from pathlib import Path

import r


def test_load_rules():
    def check():
        from loader import load_rules
        docs = load_rules(Path("rules"))
        names = [d.metadata.get("source") for d in docs]
        if names != ["loans.txt", "market.txt", "membership.txt", "spraying.txt", "storage.txt"]:
            return r.failed("load_rules", "One Document per .txt file, sorted by name, with metadata {\"source\": file name}.",
                            "['loans.txt', 'market.txt', ...]", names)
        if docs[4].page_content != Path("rules/storage.txt").read_text():
            return r.failed("load_rules", "page_content should be the whole text of the file.")
        r.passed("load_rules", "Five files, five Documents: text plus metadata, the shape every LangChain retriever expects.")
    r.task("load_rules", check)


def test_split_rules():
    def check():
        from langchain_core.documents import Document
        from loader import load_rules, split
        docs = load_rules(Path("rules"))
        if not docs:
            return r.failed("split_rules", "First load the rules (the task above).")
        chunks = split(docs)
        if len(chunks) <= len(docs):
            return r.failed("split_rules", "Split the documents with a RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap, add_start_index=True).",
                            "more chunks than documents", len(chunks))
        if any(len(c.page_content) > 300 for c in chunks):
            return r.failed("split_rules", "No chunk may be longer than size (300 characters).")
        if any("start_index" not in c.metadata or "source" not in c.metadata for c in chunks):
            return r.failed("split_rules", "Each chunk should keep its source and get a start_index: pass add_start_index=True.")
        small = split([Document("a" * 50 + " " + "b" * 50, metadata={"source": "x"})], size=60, overlap=0)
        if [len(c.page_content) for c in small] != [50, 50]:
            return r.failed("split_rules", "Use the size and overlap arguments, not fixed numbers.")
        r.passed("split_rules", f"{len(chunks)} pieces of at most 300 characters, each knowing its file and where it starts.")
    r.task("split_rules", check)
