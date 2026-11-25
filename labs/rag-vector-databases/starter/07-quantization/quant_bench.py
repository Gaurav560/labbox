"""Chapter 7: run with  python quant_bench.py   Smaller vectors: memory and recall."""
import numpy as np

from fieldbook import binary_codes, binary_search, dequantize, fake_embeddings, quantize_int8, top_k

vectors = fake_embeddings(100_000)
queries = fake_embeddings(100, seed=7)
truth = [{row for row, _ in top_k(q, vectors, k=10)} for q in queries]


def recall(search):
    return np.mean([len({row for row, _ in search(q)} & t) / 10 for q, t in zip(queries, truth)])


codes, scales = quantize_int8(vectors)
approx = dequantize(codes, scales)
bits = binary_codes(vectors)
print(f"float32: {vectors.nbytes / 1e6:6.1f} MB  recall 100% (the reference)")
print(f"int8:    {codes.nbytes / 1e6:6.1f} MB  recall {recall(lambda q: top_k(q, approx, k=10)):.1%}")
print(f"binary:  {bits.nbytes / 1e6:6.1f} MB  recall {recall(lambda q: binary_search(q, bits, vectors, k=10, candidates=10)):.1%} (bits only)")
for c in (50, 200, 1000):
    print(f"binary, {c:>4} rescored: recall {recall(lambda q: binary_search(q, bits, vectors, k=10, candidates=c)):.1%}")
