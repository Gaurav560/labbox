# Chapter 17: two finished tests, to show the shape. Run them with: python3 -m pytest -v
from money import to_paise


def test_whole_rupees():
    assert to_paise(120) == 12000


def test_rupees_and_paise():
    assert to_paise(45.5) == 4550
