"""Fieldbook, the rangers' assistant of the Vanrai Hills Wildlife Sanctuary: everything built up to chapter 3.
Each chapter adds its part at the bottom; the parts above it are finished."""
from functools import lru_cache
from pathlib import Path
import re

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
