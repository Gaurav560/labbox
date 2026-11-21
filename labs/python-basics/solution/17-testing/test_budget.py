# Chapter 17: your tests for over_budget.
from budget import over_budget


def test_exactly_on_budget_is_not_over():
    assert over_budget(500, 500) is False


def test_one_rupee_more_is_over():
    assert over_budget(501, 500) is True


def test_less_is_not_over():
    assert over_budget(120, 500) is False
