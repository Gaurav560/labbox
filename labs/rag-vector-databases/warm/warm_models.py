"""Downloads the course's two local models into FASTEMBED_CACHE_PATH at image build time, so lessons and checks
run offline: BAAI/bge-small-en-v1.5 (embeddings, 384 numbers) and Xenova/ms-marco-MiniLM-L-6-v2 (the reranker)."""
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

vectors = list(TextEmbedding("BAAI/bge-small-en-v1.5").embed(["A tiger crossed the road near the river."]))
print("embedding ready:", len(vectors[0]), "numbers")
scores = list(TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2").rerank("tiger", ["A tiger crossed the road.", "Bus timings."]))
print("reranker ready:", [round(s, 2) for s in scores])
