# Chapter 6: lists.


def top_n(numbers: list, n: int) -> list:
    return sorted(numbers, reverse=True)[:n]


def remove_duplicates(items: list) -> list:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
