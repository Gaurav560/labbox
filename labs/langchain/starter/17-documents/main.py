"""Chapter 17: run with  python main.py"""
from pathlib import Path

from loader import load_rules, split

docs = load_rules(Path("rules"))
print(f"{len(docs)} documents:", ", ".join(f"{d.metadata['source']} ({len(d.page_content)} chars)" for d in docs))
chunks = split(docs)
print(f"{len(chunks)} chunks\n")
for c in chunks:
    if c.metadata["source"] == "storage.txt":
        print(f"[{c.metadata['source']} @{c.metadata['start_index']}] {c.page_content!r}\n")
