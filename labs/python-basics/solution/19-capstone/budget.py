# Inherited from a colleague who has left. Fixed.


def over_budget(totals: dict, budgets: dict) -> list:
    """The sorted categories whose spending is above their budget."""
    result = []
    for category in budgets:
        if totals.get(category, 0) > budgets[category]:
            result.append(category)
    return sorted(result)
