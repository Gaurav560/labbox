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
    # TODO (task learn_threshold): try every rain value in the examples as a threshold and return the one with
    #   the highest accuracy(...). On a tie, keep the smaller threshold.
    return 0
