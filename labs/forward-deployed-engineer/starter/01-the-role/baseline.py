"""Week one at Deccan Shield: how long does a motor claim take today, and what does it cost the claims team?
Run it with: python baseline.py"""
import csv
from datetime import datetime

FMT = "%Y-%m-%d %H:%M"


def load_claims(path="data/claims_2026_q3.csv"):
    """Every row of Deccan Shield's export, as a dict of strings."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def days_to_decide(claim):
    """Days from received_at to decided_at, as a float; None while the claim is still open."""
    # TODO (task baseline_days): an open claim has an empty decided_at: return None for it. Otherwise turn both
    # strings into datetimes with datetime.strptime(..., FMT) and return the difference in days, as a float.
    return None


def baseline_days(claims):
    """The average days_to_decide over decided claims, rounded to 1 decimal place."""
    # TODO (task baseline_days): average days_to_decide over the claims that have a decision (skip the None ones).
    return 0.0


def adjuster_hours(claims, minutes_per_claim=35, weeks=13):
    """Hours of adjuster work a week: claims per week times minutes per claim, in hours, rounded to 1 decimal."""
    # TODO (task adjuster_hours): claims per week is len(claims) / weeks. Multiply by minutes_per_claim, divide by
    # 60 for hours, round to 1 decimal place.
    return 0.0


if __name__ == "__main__":
    claims = load_claims()
    print(f"claims in the export: {len(claims)}")
    print(f"average days to decide: {baseline_days(claims)}")
    print(f"adjuster hours a week: {adjuster_hours(claims)}")
