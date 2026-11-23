"""Chapter 10: run with  python rerank_demo.py   Hybrid search, then a cross-encoder reads every candidate."""
import time

from fieldbook import Index, load_corpus, rerank

index = Index(load_corpus())
for question in ["A night patrol cannot reach base on the radio. What happens?",
                 "Who is allowed into the core zone?",
                 "Can tourists get out of the jeep to take photos?"]:
    candidates = index.hybrid(question, k=20)
    start = time.perf_counter()
    best = rerank(question, candidates, top_n=5)
    took = (time.perf_counter() - start) * 1000
    print(question)
    print("  hybrid top 5:  ", [c["id"] for c in candidates[:5]])
    print("  reranked top 5:", [f"{c['id']} ({c['rerank']:.1f})" for c in best])
    print(f"  reranking 20 candidates took {took:.0f} ms\n")
