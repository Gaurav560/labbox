"""Claimdesk as a product: the same rules for every customer, a small adapter and a config per customer.
Run it with: python product.py"""
import csv
import json
import re
import sqlite3

CODES = {"ACC": "accident", "THF": "theft", "FLD": "flood", "FIR": "fire", "GLS": "glass"}

DECCAN = {"name": "Deccan Shield", "pilot_limit_rs": 50000, "always_refer": ["theft"], "policy_pattern": r"DS-POL-\d{5}"}
KONKAN = {"name": "Konkan Mutual", "pilot_limit_rs": 30000, "always_refer": ["theft", "fire"], "policy_pattern": r"KM/\d{2}/\d{6}"}


def from_konkan(row):
    """One row of Konkan Mutual's nightly CSV as Claimdesk's six fields (the same shape the model fills for Deccan Shield).
    Policy Ref: stripped, in capitals (None when empty). Vehicle: letters and digits only, in capitals (None when empty).
    Loss Date: DD-MM-YYYY to YYYY-MM-DD (None when empty). Cause: CODES, anything else "other". Estimate: "12,500.00" to
    12500, rounded to whole rupees (None when empty). Photos: "Y" is True, anything else False."""
    # TODO (task from_konkan): build the six fields from the row's columns, following the docstring.
    return {"policy_no": row["Policy Ref"], "vehicle_reg": row["Vehicle"], "incident_date": row["Loss Date"],
            "incident_type": "other", "amount_rs": None, "photos_attached": False}


def rules(fields, policy, config):
    """The reasons to refer, for any customer. In order: "no policy number", or "policy number not in the expected
    format" (re.fullmatch with config["policy_pattern"]), or "unknown policy" (policy is None); then, with a policy,
    "registration does not match the policy" and "incident outside the policy period"; then "no amount" or "above the
    pilot limit" (config["pilot_limit_rs"]); then f"{kind}: always referred" when the kind is in config["always_refer"]."""
    # TODO (task customer_rules): chapter 13's checks, with the numbers and lists taken from config.
    return []


def draft(reasons):
    return "pay" if not reasons else "refer"


if __name__ == "__main__":
    with open("data/konkan_policies.json", encoding="utf-8") as f:
        policies = json.load(f)
    with open("data/konkan_claims.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"{KONKAN['name']}: {len(rows)} claims from last night's export")
    for row in rows:
        fields = from_konkan(row)
        reasons = rules(fields, policies.get(fields["policy_no"]), KONKAN)
        print(f"   {row['Claim No']} {draft(reasons):<6} {reasons}")

    con = sqlite3.connect("file:data/claimdesk.db?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    with open("data/golden.json", encoding="utf-8") as f:
        golden = json.load(f)
    counts = {"pay": 0, "refer": 0}
    for case in golden:
        row = con.execute("SELECT * FROM policies WHERE policy_no = ?", (case["truth"]["policy_no"],)).fetchone()
        counts[draft(rules(case["truth"], dict(row) if row else None, DECCAN))] += 1
    print(f"{DECCAN['name']}: the golden set's 30 claims, same rules code: {counts}")
