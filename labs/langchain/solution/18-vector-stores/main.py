"""Chapter 18: run with  python main.py"""
from pathlib import Path

from loader import load_rules, split
from store import build_store, search

store = build_store(split(load_rules(Path("rules"))))
for question in ["Can I store 80 crates of onions?", "How much loan can I get for 4 acres?",
                 "Who can tell me what is wrong with my vines?", "What is the capital of France?"]:
    everything = store.similarity_search_with_score(question, k=3)
    kept = search(store, question)
    print(question)
    print("   all three:", ", ".join(f"{s:.3f} {d.metadata['source']}" for d, s in everything))
    print("   kept     :", ", ".join(f"{s:.3f} {d.metadata['source']}" for d, s in kept) or "nothing")
