"""Chapter 9: run with  python hybrid_demo.py   Meaning, words, and both."""
from fieldbook import Index, load_corpus

index = Index(load_corpus())
for question in ["CT-112", "Where do we take someone a snake has bitten?", "Can tourists get out of the jeep to take photos?"]:
    print(question)
    print("  dense (meaning):", index.dense(question, k=5))
    print("  BM25 (words):   ", index.keyword(question, k=5))
    print("  hybrid (RRF):   ", [c["id"] for c in index.hybrid(question, k=5)])
    print()
