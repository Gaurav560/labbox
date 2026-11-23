"""Chapter 6: run with  python hnsw_bench.py   An HNSW graph against brute force, with FAISS."""
import time

import faiss

from fieldbook import exact_neighbours, fake_embeddings, hnsw_index, recall_at_k

faiss.omp_set_num_threads(1)          # one CPU thread, so the timings compare like for like
vectors = fake_embeddings(100_000)
queries = fake_embeddings(200, seed=7)

start = time.perf_counter()
truth = exact_neighbours(vectors, queries, k=10)
print(f"brute force: {(time.perf_counter() - start) / len(queries) * 1000:.2f} ms a query")

start = time.perf_counter()
index = hnsw_index(vectors, m=32)
print(f"built an HNSW graph of {index.ntotal:,} vectors in {time.perf_counter() - start:.1f} s, "
      f"about {faiss.serialize_index(index).nbytes / 1e6:.0f} MB (the vectors alone: {vectors.nbytes / 1e6:.0f} MB)\n")

for ef in (16, 32, 64, 128, 256):
    index.hnsw.efSearch = ef
    start = time.perf_counter()
    _, found = index.search(queries, 10)
    ms = (time.perf_counter() - start) / len(queries) * 1000
    print(f"efSearch {ef:>3}: recall {recall_at_k(found, truth):6.1%}, {ms:.3f} ms a query")
