"""Fieldbook, the rangers' assistant of the Vanrai Hills Wildlife Sanctuary: everything built up to chapter 10.
Each chapter adds its part at the bottom; the parts above it are finished."""
from functools import lru_cache
from pathlib import Path
import json
import math
import re

from qdrant_client import QdrantClient, models
import faiss
import numpy as np

# ---------------------------------------------------------------- chapter 1: words and prompts

STOPWORDS = set("""a an and are as at be by can do does for from has have how i if in is it its me my of on or our
should so that the their them then there they this to was we what when where which who why will with you your""".split())


def load_sections(path="data/manual.md"):
    """The manual's sections: [{"id": "FM-4.2", "title": "Meeting a tiger", "text": "..."}, ...].
    (You will write this yourself in chapter 4, as section_chunks.)"""
    sections = []
    for block in Path(path).read_text().split("\n## ")[1:]:
        heading, _, body = block.partition("\n")
        number, _, title = heading.partition(" ")
        sections.append({"id": number, "title": title, "text": " ".join(body.split())})
    return sections


def words(text):
    """The words of a text that carry meaning, in lower case: "Meeting a tiger!" gives {"meeting", "tiger"}."""
    return {w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if len(w) > 2 and w not in STOPWORDS}


def keyword_search(question, sections, k=3):
    """The k sections that share the most words with the question, best first. Sections with no shared word are
    left out; equal scores keep the manual's order."""
    asked = words(question)
    scored = []
    for position, section in enumerate(sections):
        shared = len(asked & words(section["title"] + " " + section["text"]))
        if shared > 0:
            scored.append((shared, position, section))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [section for _, _, section in scored[:k]]


SYSTEM = ("You are Fieldbook, the assistant for rangers of the Vanrai Hills Wildlife Sanctuary. Answer only from the "
          "manual sections you are given, in at most three sentences, and name the section you used, like [FM-4.2]. "
          "If the sections do not answer the question, say that the manual does not cover it.")


def build_prompt(question, sections):
    """The messages for the model: SYSTEM, then one user message with the sections and the question."""
    context = "\n\n".join(f"[{s['id']}] {s['title']}\n{s['text']}" for s in sections)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Manual sections:\n\n{context}\n\nQuestion: {question}"},
    ]

# ---------------------------------------------------------------- chapter 2: embeddings


@lru_cache(maxsize=1)
def model():
    """The embedding model, BAAI/bge-small-en-v1.5: 33 million weights, on your own CPU. Loaded once."""
    from fastembed import TextEmbedding
    return TextEmbedding("BAAI/bge-small-en-v1.5")


def embed(texts):
    """One row of 384 numbers for each text, as a float32 matrix (len(texts) rows, 384 columns)."""
    return np.array(list(model().embed(list(texts))), dtype=np.float32)


def cosine(a, b):
    """How alike two vectors point: 1.0 the same direction, 0.0 unrelated, -1.0 opposite."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ---------------------------------------------------------------- chapter 3: nearest neighbours


def normalize(m):
    """Every row (or a single vector) scaled to length 1, so that a dot product is the cosine."""
    m = np.asarray(m, dtype=np.float32)
    return m / np.linalg.norm(m, axis=-1, keepdims=True)


def top_k(query, matrix, k=3):
    """The k rows of a normalized matrix closest to a normalized query, as [(row, score), ...], best first."""
    scores = matrix @ query
    k = min(k, len(scores))
    best = np.argpartition(-scores, k - 1)[:k]
    best = best[np.argsort(-scores[best])]
    return [(int(i), float(scores[i])) for i in best]


def fake_embeddings(n, dim=384, seed=0):
    """n random vectors shaped like real embeddings, for measuring speed at sizes the sanctuary's own documents
    will never reach. Real embeddings use only a few directions of their 384 (texts about similar things sit close
    together), so these are made in 24 dimensions, grouped around 500 topics, then spread into 384 and given length 1."""
    rng = np.random.default_rng(seed)
    basis = np.random.default_rng(42).standard_normal((24, dim), dtype=np.float32)   # the same for every call
    topics = np.random.default_rng(43).standard_normal((500, 24), dtype=np.float32)
    out = np.empty((n, dim), dtype=np.float32)
    for start in range(0, n, 50_000):
        stop = min(n, start + 50_000)
        latent = topics[rng.integers(0, 500, stop - start)] + rng.standard_normal((stop - start, 24), dtype=np.float32)
        out[start:stop] = latent @ basis + 0.5 * rng.standard_normal((stop - start, dim), dtype=np.float32)
    return normalize(out)

# ---------------------------------------------------------------- chapter 4: chunks


def word_chunks(text, size=120, overlap=20):
    """The text cut into pieces of `size` words; each piece repeats the last `overlap` words of the one before."""
    tokens = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(tokens), step):
        chunks.append(" ".join(tokens[start:start + size]))
        if start + size >= len(tokens):
            break
    return chunks


def section_chunks(markdown):
    """One chunk per "## " section of a Markdown text: {"id": "FM-4.2", "title": "Meeting a tiger", "text": "..."}."""
    chunks = []
    for block in markdown.split("\n## ")[1:]:
        heading, _, body = block.partition("\n")
        number, _, title = heading.partition(" ")
        chunks.append({"id": number, "title": title, "text": " ".join(body.split())})
    return chunks


def load_corpus(manual="data/manual.md", reports="data/reports.jsonl"):
    """Every chunk Fieldbook searches: the manual's sections and the patrol reports, each with its metadata."""
    chunks = [dict(c, kind="manual", zone="all") for c in section_chunks(Path(manual).read_text())]
    for line in Path(reports).read_text().splitlines():
        r = json.loads(line)
        chunks.append({"id": r["id"], "title": f"Patrol report {r['id']}, {r['date']}, beat {r['beat']}",
                       "text": r["text"], "kind": "report", "zone": r["zone"], "beat": r["beat"], "date": r["date"]})
    return chunks


def chunk_text(chunk):
    """What gets embedded and searched: the title, then the text."""
    return chunk["title"] + ". " + chunk["text"]


def load_questions(path="data/questions.json"):
    """The test questions, each with the ids of the chunks that answer it."""
    return json.loads(Path(path).read_text())

# ---------------------------------------------------------------- chapter 5: IVF


def train_centroids(vectors, n_lists, iterations=8, seed=0):
    """k-means: n_lists centre points, each the average of the vectors nearest to it (Lloyd's algorithm)."""
    rng = np.random.default_rng(seed)
    centroids = vectors[rng.choice(len(vectors), n_lists, replace=False)].copy()
    for _ in range(iterations):
        nearest = np.argmax(vectors @ centroids.T, axis=1)
        sums = np.zeros_like(centroids)
        np.add.at(sums, nearest, vectors)
        counts = np.bincount(nearest, minlength=n_lists)
        moved = counts > 0
        centroids[moved] = sums[moved] / counts[moved, None]
        centroids = normalize(centroids)
    return centroids


def build_lists(vectors, centroids):
    """The inverted lists: for each centroid, the rows of `vectors` whose nearest centroid it is."""
    nearest = np.argmax(vectors @ centroids.T, axis=1)
    return [np.flatnonzero(nearest == c) for c in range(len(centroids))]


def ivf_search(query, vectors, centroids, lists, k=10, nprobe=4):
    """Search only the nprobe lists whose centroids are closest to the query. [(row, score), ...], best first."""
    probe = np.argsort(-(centroids @ query))[:nprobe]
    candidates = np.concatenate([lists[c] for c in probe])
    if len(candidates) == 0:
        return []
    scores = vectors[candidates] @ query
    best = np.argsort(-scores)[:k]
    return [(int(candidates[i]), float(scores[i])) for i in best]

# ---------------------------------------------------------------- chapter 6: HNSW


def exact_neighbours(vectors, queries, k=10):
    """The true k nearest rows for every query, by brute force: the answer key for measuring recall."""
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index.search(queries, k)[1]


def hnsw_index(vectors, m=32, ef_construction=64):
    """A FAISS HNSW graph over the vectors: m links per node, inner product (cosine for length-1 vectors)."""
    index = faiss.IndexHNSWFlat(vectors.shape[1], m, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = ef_construction
    index.add(vectors)
    return index


def recall_at_k(found, truth):
    """For each query, the share of its true neighbours that were found; averaged over all queries."""
    k = len(truth[0])
    return float(np.mean([len(set(f[:k]) & set(t)) / k for f, t in zip(found, truth)]))


def smallest_ef(index, queries, truth, k=10, target=0.95, choices=(16, 32, 64, 128, 256, 512)):
    """The smallest efSearch in `choices` whose recall reaches the target, or None if none does."""
    for ef in choices:
        index.hnsw.efSearch = ef
        _, found = index.search(queries, k)
        if recall_at_k(found, truth) >= target:
            return ef
    return None

# ---------------------------------------------------------------- chapter 7: quantization


def quantize_int8(m):
    """Every column squeezed into whole numbers from -127 to 127. Returns (codes as int8, one float32 scale per
    column); codes * scales is close to m, in a quarter of the memory."""
    scales = np.abs(m).max(axis=0) / 127
    scales[scales == 0] = 1
    codes = np.round(m / scales).astype(np.int8)
    return codes, scales.astype(np.float32)


def dequantize(codes, scales):
    """Back from int8 to approximate float32 values."""
    return codes.astype(np.float32) * scales


def binary_codes(m):
    """One bit per number: 1 where it is above zero. 384 numbers become 48 bytes."""
    return np.packbits(np.atleast_2d(m) > 0, axis=1)


def hamming(query_bits, codes):
    """How many bits differ between the query's bits and every row of codes."""
    return np.unpackbits(np.bitwise_xor(codes, query_bits), axis=1).sum(axis=1)


def binary_search(query, codes, vectors, k=10, candidates=100):
    """Shortlist by Hamming distance on the bits, then rescore the shortlist with the full vectors."""
    distances = hamming(binary_codes(query)[0], codes)
    candidates = min(candidates, len(distances))
    shortlist = np.argpartition(distances, candidates - 1)[:candidates]
    scores = vectors[shortlist] @ query
    best = np.argsort(-scores)[:k]
    return [(int(shortlist[i]), float(scores[i])) for i in best]

# ---------------------------------------------------------------- chapter 8: Qdrant

COLLECTION = "fieldbook"


def make_store(chunks, vectors):
    """A Qdrant collection holding every chunk: its vector, and the chunk itself as the payload."""
    client = QdrantClient(":memory:")
    client.create_collection(COLLECTION, vectors_config=models.VectorParams(size=vectors.shape[1], distance=models.Distance.COSINE))
    client.upsert(COLLECTION, points=[models.PointStruct(id=i, vector=v.tolist(), payload=c)
                                      for i, (c, v) in enumerate(zip(chunks, vectors))])
    return client


def filtered_search(client, query_vector, k=5, kind=None, zone=None):
    """The k nearest chunks, keeping only those whose payload matches kind and zone when they are given.
    Each result is the chunk's payload with its "score" added."""
    conditions = [models.FieldCondition(key=key, match=models.MatchValue(value=value))
                  for key, value in (("kind", kind), ("zone", zone)) if value is not None]
    hits = client.query_points(COLLECTION, query=query_vector.tolist(), limit=k,
                               query_filter=models.Filter(must=conditions) if conditions else None).points
    return [dict(hit.payload, score=hit.score) for hit in hits]

# ---------------------------------------------------------------- chapter 9: hybrid search


def tokens(text):
    """Every word of a text, in lower case, codes like ct-117 kept whole."""
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


def bm25_scores(query, docs, k1=1.5, b=0.75):
    """BM25: one score per document (docs is a list of token lists) for the query's tokens."""
    n = len(docs)
    average = sum(len(d) for d in docs) / n
    scores = np.zeros(n)
    for term in set(query):
        df = sum(1 for d in docs if term in d)
        if df == 0:
            continue
        idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
        for i, d in enumerate(docs):
            tf = d.count(term)
            if tf:
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / average))
    return scores


def rrf(rankings, k=60):
    """Reciprocal rank fusion: ids from several rankings (each best first), merged by the sum of 1 / (k + rank)."""
    fused = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            fused[item] = fused.get(item, 0.0) + 1 / (k + rank)
    return sorted(fused, key=lambda item: -fused[item])


class Index:
    """Everything Fieldbook searches, ready: the chunks, their normalized vectors and their tokens."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.vectors = normalize(embed([chunk_text(c) for c in chunks]))
        self.tokens = [tokens(chunk_text(c)) for c in chunks]

    def dense(self, question, k=20):
        return [self.chunks[i]["id"] for i, _ in top_k(normalize(embed([question])[0]), self.vectors, k)]

    def keyword(self, question, k=20):
        scores = bm25_scores(tokens(question), self.tokens)
        return [self.chunks[i]["id"] for i in np.argsort(-scores)[:k] if scores[i] > 0]

    def hybrid(self, question, k=5):
        by_id = {c["id"]: c for c in self.chunks}
        return [by_id[i] for i in rrf([self.dense(question), self.keyword(question)])[:k]]

# ---------------------------------------------------------------- chapter 10: reranking


@lru_cache(maxsize=1)
def reranker():
    """A cross-encoder, ms-marco-MiniLM-L-6-v2: reads the question and a chunk together and scores the pair."""
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    return TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2")


def rerank(question, chunks, top_n=5):
    """The chunks sorted by the cross-encoder's score, best first, at most top_n, each with "rerank" added."""
    scores = list(reranker().rerank(question, [chunk_text(c) for c in chunks]))
    order = np.argsort(scores)[::-1][:top_n]
    return [dict(chunks[i], rerank=float(scores[i])) for i in order]


def two_stage(question, index, first=20, final=5):
    """Fast and wide, then slow and careful: hybrid search for `first` candidates, reranked down to `final`."""
    return rerank(question, index.hybrid(question, k=first), top_n=final)
