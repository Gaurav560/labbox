"""Chapter 5: run with  python ivf_bench.py   Recall and speed of IVF against brute force."""
import time

import numpy as np

from fieldbook import build_lists, fake_embeddings, ivf_search, top_k, train_centroids

vectors = fake_embeddings(100_000)
queries = fake_embeddings(50, seed=7)
truth = [{row for row, _ in top_k(q, vectors, k=10)} for q in queries]

start = time.perf_counter()
for q in queries:
    top_k(q, vectors, k=10)
brute = (time.perf_counter() - start) / len(queries) * 1000
print(f"brute force: recall 100%, {brute:.2f} ms a query\n")

start = time.perf_counter()
centroids = train_centroids(vectors, n_lists=316)
lists = build_lists(vectors, centroids)
print(f"trained 316 lists in {time.perf_counter() - start:.1f} s; sizes from {min(map(len, lists))} to {max(map(len, lists))}\n")

for nprobe in (1, 4, 16, 64):
    start = time.perf_counter()
    recall = np.mean([len({row for row, _ in ivf_search(q, vectors, centroids, lists, k=10, nprobe=nprobe)} & t) / 10
                      for q, t in zip(queries, truth)])
    ms = (time.perf_counter() - start) / len(queries) * 1000
    print(f"nprobe {nprobe:>3}: recall {recall:5.0%}, {ms:6.2f} ms a query, searches {nprobe / 316:5.1%} of the lists")
