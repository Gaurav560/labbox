# Chapter 7: dictionaries.


def count_letters(text: str) -> dict:
    counts = {}
    for ch in text.lower():
        if ch.isalpha():
            counts[ch] = counts.get(ch, 0) + 1
    return counts


def total_by_category(expenses: list) -> dict:
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return totals
