# Chapter 16: Pocket's main program. Its money helpers belong in a module of their own, money.py.
from money import format_price, to_paise

spent = [120, 45.5, 1250]
for amount in spent:
    print(format_price(amount), "=", to_paise(amount), "paise")
