# Chapter 3: numbers and text. Pocket needs to do sums with money and show amounts nicely.


def average(amounts):
    return round(sum(amounts) / len(amounts), 2)


def format_price(amount):
    return f"₹{amount:,.2f}"
