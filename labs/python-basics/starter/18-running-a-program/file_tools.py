# Chapter 18: a finished copy of chapter 14's read_totals, so this program does not depend on your chapter 14.
import csv


def read_totals(path):
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


def save_lines(path, lines):
    with open(path, "w") as f:
        for line in lines:
            f.write(line + "\n")
    return len(lines)
