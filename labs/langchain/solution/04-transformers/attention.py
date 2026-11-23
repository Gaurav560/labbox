"""Two small pieces of a transformer, in plain Python: softmax with a temperature, and attention weights."""
import math


def softmax(scores: list[float], temperature: float = 1.0) -> list[float]:
    top = max(scores)
    exps = [math.exp((s - top) / temperature) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


def attention(query: list[float], keys: list[list[float]]) -> list[float]:
    scale = math.sqrt(len(query))
    scores = [sum(q * k for q, k in zip(query, key)) / scale for key in keys]
    return softmax(scores)
