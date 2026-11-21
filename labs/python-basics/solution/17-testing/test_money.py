# Chapter 17: your tests for format_price.
from money import format_price


def test_small_amount():
    assert format_price(5) == "₹5.00"


def test_thousands():
    assert format_price(1250.5) == "₹1,250.50"


def test_rounds_to_two_decimals():
    assert format_price(999.999) == "₹1,000.00"
