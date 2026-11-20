# Chapter 11: files.
import csv


def read_totals(path: str) -> dict:
    totals = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                amount = float(row["amount"])
            except (TypeError, ValueError):
                continue
            category = row["category"]
            totals[category] = totals.get(category, 0) + amount
    return {k: round(v, 2) for k, v in totals.items()}


def save_lines(path: str, lines: list) -> int:
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")
    return len(lines)
