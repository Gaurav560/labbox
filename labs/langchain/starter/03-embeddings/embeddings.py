"""Meaning as numbers. vectors.json holds real embeddings from OpenAI's text-embedding-3-small (256 numbers each)
for the co-op's frequent questions and a few new ones."""
import json
import math
from pathlib import Path

VECTORS = json.loads(Path(__file__).with_name("vectors.json").read_text())


def cosine(a: list[float], b: list[float]) -> float:
    # TODO (task cosine): the cosine similarity: the dot product of a and b, divided by the product of their lengths
    #   (the length of a is the square root of the sum of its squares).
    return 0.0


def closest_question(query: list[float], faq: dict[str, list[float]]) -> str:
    # TODO (task closest_question): return the FAQ question (a key of faq) whose vector has the highest cosine with query.
    return ""
