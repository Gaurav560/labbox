# Chapter 16: Pocket's main program. Its money helpers belong in a module of their own, money.py.
# TODO (task money_module): create money.py with format_price(amount) and to_paise(amount), then import
# both here instead of defining format_price in this file. The output must stay exactly the same.


def format_price(amount):
    return f"₹{amount:,.2f}"


spent = [120, 45.5, 1250]
for amount in spent:
    print(format_price(amount), "=", round(amount * 100), "paise")
