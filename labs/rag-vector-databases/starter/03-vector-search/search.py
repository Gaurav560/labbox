"""Chapter 3: run with  python search.py  or  python search.py "your question"
Embeds every manual section once, then finds the closest sections to a question."""
import sys
import time

from fieldbook import embed, load_sections, normalize, top_k

question = sys.argv[1] if len(sys.argv) > 1 else "What should I do if a big cat is right in front of me?"
sections = load_sections()
start = time.perf_counter()
matrix = normalize(embed([s["title"] + ". " + s["text"] for s in sections]))
print(f"Embedded {len(sections)} sections in {time.perf_counter() - start:.2f} s: a {matrix.shape[0]} x {matrix.shape[1]} matrix\n")

start = time.perf_counter()
query = normalize(embed([question])[0])
hits = top_k(query, matrix, k=3)
print(f"{question!r} ({(time.perf_counter() - start) * 1000:.1f} ms, the question's embedding included)")
for row, score in hits:
    print(f"  {score:.3f}  [{sections[row]['id']}] {sections[row]['title']}")
