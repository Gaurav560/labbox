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
    if not claim["decided_at"]:
        return None
    received = datetime.strptime(claim["received_at"], FMT)
    decided = datetime.strptime(claim["decided_at"], FMT)
    return (decided - received).total_seconds() / 86400


def baseline_days(claims):
    """The average days_to_decide over decided claims, rounded to 1 decimal place."""
    days = [d for d in (days_to_decide(c) for c in claims) if d is not None]
    return round(sum(days) / len(days), 1)


def adjuster_hours(claims, minutes_per_claim=35, weeks=13):
    """Hours of adjuster work a week: claims per week times minutes per claim, in hours, rounded to 1 decimal."""
    return round(len(claims) / weeks * minutes_per_claim / 60, 1)


if __name__ == "__main__":
    claims = load_claims()
    print(f"claims in the export: {len(claims)}")
    print(f"average days to decide: {baseline_days(claims)}")
    print(f"adjuster hours a week: {adjuster_hours(claims)}")
