# Chapter 10: tuples and sets.


def common_items(a, b):
    return sorted(set(a) & set(b))


def min_max(numbers):
    if not numbers:
        return (None, None)
    return (min(numbers), max(numbers))
