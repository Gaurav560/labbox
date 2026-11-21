# Chapter 19: the monthly report. Read the contract in the lesson first.
import csv


def monthly_report(path):
    good, bad_lines = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_no = reader.line_num  # the real line in the file (csv skips blank lines by itself)
            category = (row.get("category") or "").strip()
            try:
                amount = float(row.get("amount"))
            except (TypeError, ValueError):
                amount = None
            if not category or amount is None:
                bad_lines.append(line_no)
                continue
            good.append((category, amount))
    per_category = {}
    for category, amount in good:
        per_category[category] = per_category.get(category, 0) + amount
    total = round(sum(a for _, a in good), 2)
    count = len(good)
    biggest = max(good, key=lambda g: g[1]) if good else None
    return {
        "total": total,
        "count": count,
        "average": round(total / count, 2) if count else 0.0,
        "biggest": {"category": biggest[0], "amount": biggest[1]} if biggest else None,
        "per_category": {k: round(v, 2) for k, v in per_category.items()},
        "bad_lines": bad_lines,
    }
