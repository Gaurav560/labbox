# Chapter 2: numbers and text.


def average(marks: list) -> float:
    if not marks:
        return 0.0
    return round(sum(marks) / len(marks), 2)


def format_price(amount: float) -> str:
    return f"₹{amount:,.2f}"
