# Chapter 4: loops.


def count_above(numbers: list, limit: int) -> int:
    count = 0
    for n in numbers:
        if n > limit:
            count += 1
    return count


def first_negative(numbers: list):
    for n in numbers:
        if n < 0:
            return n
    return None
