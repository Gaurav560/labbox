# Chapter 8: lists.


def top_n(numbers, n):
    return sorted(numbers, reverse=True)[:n]


def remove_duplicates(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
