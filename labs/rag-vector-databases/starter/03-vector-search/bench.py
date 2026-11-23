"""Chapter 3: run with  python bench.py   How long does brute force take as the collection grows?"""
import time

import numpy as np

from fieldbook import fake_embeddings, normalize, top_k

queries = normalize(np.random.default_rng(1).standard_normal((20, 384), dtype=np.float32))
for n in (10_000, 100_000, 300_000):
    vectors = fake_embeddings(n)
    top_k(queries[0], vectors, k=10)                   # warm up
    start = time.perf_counter()
    for q in queries:
        top_k(q, vectors, k=10)
    ms = (time.perf_counter() - start) / len(queries) * 1000
    print(f"{n:>9,} vectors  {vectors.nbytes / 1e6:7.1f} MB  {ms:7.2f} ms a query")
    del vectors
