# Chapter 10: errors.


def to_number(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a number") from None


def safe_sum(values: list) -> tuple:
    total = 0.0
    bad = []
    for v in values:
        try:
            total += to_number(v)
        except ValueError:
            bad.append(v)
    return total, bad
