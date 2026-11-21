# Chapter 6: finding bugs. Both functions run without crashing, and both give a wrong answer.


def daily_total(amounts):
    """Add up one day's expenses."""
    # TODO (task fix_daily_total): daily_total([120, 80, 100]) should be 300, but it says 180. Find out why.
    total = 0
    for i in range(len(amounts)):
        total = total + amounts[i]
    return total


def over_budget(amounts, budget):
    """True only when the day's spending is more than the budget."""
    # TODO (task fix_over_budget): spending exactly the budget is fine, but this says it is over. Find out why.
    spent = sum(amounts)
    left = budget - spent
    return left < 0


if __name__ == "__main__":
    print(daily_total([120, 80, 100]))
    print(over_budget([300, 200], 500))
