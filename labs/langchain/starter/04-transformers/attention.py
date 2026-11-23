"""Two small pieces of a transformer, in plain Python: softmax with a temperature, and attention weights."""
import math


def softmax(scores: list[float], temperature: float = 1.0) -> list[float]:
    # TODO (task softmax_temperature): divide every score by the temperature, take math.exp of each, and divide each
    #   by their sum, so the results are positive and add up to 1. (Subtract the largest score first, for safety.)
    return scores


def attention(query: list[float], keys: list[list[float]]) -> list[float]:
    # TODO (task attention_weights): score each key by its dot product with the query, divided by the square root of
    #   the vector length (len(query)), then turn the scores into weights with softmax(...).
    return [0.0 for _ in keys]
