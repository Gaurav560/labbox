# Inherited from a colleague who has left. The tests in production are failing.
# TODO (task fix_budget): find out how over_budget fails, and fix it.


def over_budget(totals: dict, budgets: dict) -> list:
    """The sorted categories whose spending is above their budget."""
    result = []
    for category in budgets:
        if totals[category] >= budgets[category]:
            result.append(category)
    return result.sort()
