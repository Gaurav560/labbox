# Pocket's money helpers, in a module of their own.


def format_price(amount):
    return f"₹{amount:,.2f}"


def to_paise(amount):
    return round(amount * 100)
