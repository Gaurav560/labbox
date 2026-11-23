"""Chapter 2: run with  python similar.py   How alike are these sentences, as the model sees them?"""
import time

from fieldbook import cosine, embed, model

pairs = [
    ("A tiger crossed the path.", "A big cat walked across the trail."),
    ("A tiger crossed the path.", "A leopard crossed the road."),
    ("A tiger crossed the path.", "Change the camera trap batteries every 21 days."),
    ("Change the camera trap batteries every 21 days.", "How often do the trail cameras need new cells?"),
    ("The core zone is closed to visitors.", "Tourists may not enter the core zone."),
    ("The core zone is closed to visitors.", "The core zone is open to visitors."),
]
start = time.perf_counter()
model()
print(f"model loaded in {time.perf_counter() - start:.2f} s")
start = time.perf_counter()
vectors = embed([s for pair in pairs for s in pair])
took = time.perf_counter() - start
print(f"{len(vectors)} sentences -> {vectors.shape[1]} numbers each, in {took * 1000:.0f} ms\n")
for n, (a, b) in enumerate(pairs):
    print(f"{cosine(vectors[2 * n], vectors[2 * n + 1]):.3f}  {a!r} / {b!r}")
print("\nThe first 8 numbers of the first sentence:", [round(float(x), 3) for x in vectors[0][:8]])
