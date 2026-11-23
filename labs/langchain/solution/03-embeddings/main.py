"""Chapter 3: run with  python main.py"""
from embeddings import VECTORS, closest_question, cosine

faq, queries = VECTORS["faq"], VECTORS["queries"]
for query, vector in queries.items():
    best = closest_question(vector, faq)
    print(f"{query!r:44} -> {best!r} ({cosine(vector, faq[best]):.3f})")
