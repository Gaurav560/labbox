"""Scoping the pilot: which claims Claimdesk handles first, and a goal everyone can measure.
Run it with: python scope.py"""
import csv


def load_claims(path="data/claims_2026_q3.csv"):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


GOAL = {
    "metric": "days to decide a two-wheeler email claim",
    "baseline": 12.2,
    "target": 5,
    "unit": "days",
    "by": "2026-12-31",
}
PARTS = ["metric", "baseline", "target", "unit", "by"]


def pilot_slice(claims):
    """The claims the pilot handles: two-wheelers, sent by email, for Rs 50,000 or less."""
    return [c for c in claims
            if c["vehicle"] == "two-wheeler" and c["channel"] == "email" and int(c["amount_rs"]) <= 50000]


def missing_parts(goal):
    """The parts a measurable goal still lacks, in the order of PARTS."""
    missing = []
    for part in PARTS:
        value = goal.get(part)
        if value in (None, ""):
            missing.append(part)
        elif part in ("baseline", "target") and not isinstance(value, (int, float)):
            missing.append(part)
    return missing


if __name__ == "__main__":
    claims = load_claims()
    pilot = pilot_slice(claims)
    print(f"all claims: {len(claims)}, in the pilot: {len(pilot)} ({len(pilot) / len(claims):.0%})")
    print("missing from the goal:", missing_parts(GOAL) or "nothing")
    print("missing from 'make claims faster':", missing_parts({"metric": "make claims faster"}))
