# Chapter 15: classes. Pocket's own kinds of values: one Expense, and a Pocket that holds many of them.


class Expense:
    def __init__(self, name, amount, category="other"):
        self.name = name
        self.amount = amount
        self.category = category

    def label(self):
        return f"{self.name}: ₹{self.amount:,.2f} ({self.category})"


class Pocket:
    def __init__(self):
        self.expenses = []

    def add(self, expense):
        self.expenses.append(expense)

    def total(self):
        return sum(e.amount for e in self.expenses)

    def biggest(self):
        if not self.expenses:
            return None
        return max(self.expenses, key=lambda e: e.amount)
