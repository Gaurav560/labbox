# Chapter 11: sorting and comprehensions. One week of Pocket's expenses.
WEEK = [
    {"name": "chai", "amount": 120},
    {"name": "rent", "amount": 9000},
    {"name": "bus", "amount": 40},
    {"name": "lunch", "amount": 120},
    {"name": "phone", "amount": 599},
]


def large_expenses(expenses, limit):
    return [e["name"] for e in expenses if e["amount"] > limit]


def by_amount(expenses):
    return sorted(expenses, key=lambda e: (-e["amount"], e["name"]))
