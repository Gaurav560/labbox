"""The real export, as Deccan Shield's branch IT team sends it every Monday: three date formats, rupees written four
ways, some rows twice and some with no amount. Clean it before anything reads it. Run it with: python clean.py"""
import csv
from collections import Counter
from datetime import datetime

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"]  # 2026-07-02, 02/07/2026 (day first), 02 Jul 2026


def load_raw(path="data/claims_export_raw.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_date(text):
    """A date from any of the export's three formats (day first, as in India), or None if none fits."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_amount(text):
    """Whole rupees as an int from "Rs 21,500", "₹ 3,37,500", "34500.00" or "36500"; None when blank or unreadable."""
    # TODO (task parse_amount): take away "Rs", "₹" and every comma, then strip spaces. Nothing left: None. Otherwise
    # read the rest as a float (so "34500.00" works) and return it as an int; text that is not a number gives None.
    return None


def clean_export(rows):
    """(clean, rejected). clean: one dict per claim, the first copy only, with claim_id, received (a date), amount_rs
    (an int), vehicle and channel. rejected: (claim_id, reason) pairs, reason "duplicate", "bad date" or "no amount"."""
    # TODO (task clean_export): go through the rows in order. A claim_id seen before is rejected as "duplicate".
    # Otherwise remember the id, then parse the date and the amount: None means rejected, as "bad date" or "no amount"
    # (check the date first). Everything else becomes a clean dict.
    return [], []


if __name__ == "__main__":
    raw = load_raw()
    clean, rejected = clean_export(raw)
    print(f"rows in the export: {len(raw)}")
    print(f"clean claims: {len(clean)}")
    print(f"rejected: {len(rejected)}", dict(Counter(reason for _, reason in rejected)))
    for text in ["Rs 21,500", "₹ 3,37,500", "34500.00", "36500", ""]:
        print(f"{text!r:>14} -> {parse_amount(text)!r}")
