# Chapter 17: Pocket's money helpers (they work). Your job is to prove it, with tests.


def format_price(amount):
    return f"₹{amount:,.2f}"


def to_paise(amount):
    return round(amount * 100)
