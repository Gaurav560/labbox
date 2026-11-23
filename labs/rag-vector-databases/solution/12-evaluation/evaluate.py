"""Chapter 12: run with  python evaluate.py   Four ways to retrieve, measured on the 26 test questions."""
import time

from fieldbook import Index, hit_rate, keyword_search, load_corpus, load_questions, mrr, rerank

chunks = load_corpus()
index = Index(chunks)
questions = load_questions()
expected = [q["answers"] for q in questions]

pipelines = {
    "keywords (chapter 1)": lambda q: [c["id"] for c in keyword_search(q, chunks, k=5)],
    "dense (chapter 3)": lambda q: index.dense(q, k=5),
    "hybrid (chapter 9)": lambda q: [c["id"] for c in index.hybrid(q, k=5)],
    "hybrid + rerank (chapter 10)": lambda q: [c["id"] for c in rerank(q, index.hybrid(q, k=20), top_n=5)],
}
print(f"{len(questions)} questions\n")
print(f"{'pipeline':30} {'hit@1':>6} {'hit@5':>6} {'MRR':>6} {'ms/q':>6}")
for name, run in pipelines.items():
    start = time.perf_counter()
    results = [run(q["question"]) for q in questions]
    ms = (time.perf_counter() - start) / len(questions) * 1000
    print(f"{name:30} {hit_rate(results, expected, k=1):6.0%} {hit_rate(results, expected, k=5):6.0%} "
          f"{mrr(results, expected):6.2f} {ms:6.0f}")
    misses = [q["question"] for q, got in zip(questions, results) if not set(got[:5]) & set(q["answers"])]
    for m in misses:
        print(f"{'':4}missed: {m}")
