"""Meaning as numbers. vectors.json holds real embeddings from OpenAI's text-embedding-3-small (256 numbers each)
for the co-op's frequent questions and a few new ones."""
import json
import math
from pathlib import Path

VECTORS = json.loads(Path(__file__).with_name("vectors.json").read_text())


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def closest_question(query: list[float], faq: dict[str, list[float]]) -> str:
    return max(faq, key=lambda question: cosine(query, faq[question]))
