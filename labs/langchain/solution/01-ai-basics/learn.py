"""Way 2: the program learns the rule from examples.

Each example is one morning on a member's farm: millimetres of rain overnight, and whether the farmer then skipped
irrigating that day. Nobody tells the program where the line is; it finds the line that explains the examples best.
"""

EXAMPLES = [(0, False), (2, False), (3, False), (5, False), (6, False), (8, True), (9, False), (11, True),
            (12, True), (15, True), (18, True), (25, True)]


def accuracy(threshold: float, examples: list[tuple[float, bool]]) -> float:
    """The share of examples the rule "skip when rain >= threshold" gets right."""
    right = sum(1 for rain, skipped in examples if (rain >= threshold) == skipped)
    return right / len(examples)


def learn_threshold(examples: list[tuple[float, bool]]) -> float:
    best, best_accuracy = 0, -1.0
    for candidate in sorted(rain for rain, _ in examples):
        score = accuracy(candidate, examples)
        if score > best_accuracy:
            best, best_accuracy = candidate, score
    return best
