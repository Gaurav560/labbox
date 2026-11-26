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
    # TODO (task pilot_slice): keep a claim only if all three hold: vehicle is "two-wheeler", channel is "email",
    # and int(amount_rs) is 50000 or less. Return the list, in the same order.
    return []


def missing_parts(goal):
    """The parts a measurable goal still lacks, in the order of PARTS."""
    # TODO (task measurable_goal): a part is missing when its key is absent, or empty. "baseline" and "target" must
    # also be numbers (int or float), or they count as missing. Return the missing names, in PARTS order.
    return []


if __name__ == "__main__":
    claims = load_claims()
    pilot = pilot_slice(claims)
    print(f"all claims: {len(claims)}, in the pilot: {len(pilot)} ({len(pilot) / len(claims):.0%})")
    print("missing from the goal:", missing_parts(GOAL) or "nothing")
    print("missing from 'make claims faster':", missing_parts({"metric": "make claims faster"}))
