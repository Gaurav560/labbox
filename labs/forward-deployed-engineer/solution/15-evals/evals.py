"""Evals: how often each version of Claimdesk is right, field by field, and a gate that stops regressions.
Run it with: python evals.py"""
import json

FIELDS = ["policy_no", "vehicle_reg", "incident_date", "incident_type", "amount_rs", "photos_attached"]


def load_golden(path="data/golden.json"):
    """The golden set: 30 real claim emails, each with the fields an adjuster wrote down (the truth)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_run(path):
    """One run of Claimdesk over the golden set: email_id -> the fields it read (None when it could not read the email)."""
    with open(path, encoding="utf-8") as f:
        return {row["email_id"]: row["fields"] for row in json.load(f)}


def field_match(field, got, truth):
    """True when Claimdesk's value counts as right. Strict, because everything after it is exact: the policy lookup is
    SQL, the date check is a comparison. None matches only None; text must be the same text (outer spaces ignored);
    a yes/no must be a real bool; numbers must be equal ints."""
    if truth is None:
        return got is None
    if got is None:
        return False
    if isinstance(truth, bool):
        return got is truth
    if isinstance(truth, str):
        return isinstance(got, str) and got.strip() == truth
    return isinstance(got, int) and not isinstance(got, bool) and got == truth


def eval_report(golden, run):
    """{field: percent right, 1 decimal} for each of FIELDS, plus "all_fields": the percent of emails with every field
    right. An email the run could not read (None) is wrong on every field."""
    right = {f: 0 for f in FIELDS}
    whole = 0
    for case in golden:
        got = run.get(case["email_id"])
        oks = [got is not None and field_match(f, got[f], case["truth"][f]) for f in FIELDS]
        for f, ok in zip(FIELDS, oks):
            right[f] += ok
        whole += all(oks)
    n = len(golden)
    report = {f: round(right[f] / n * 100, 1) for f in FIELDS}
    report["all_fields"] = round(whole / n * 100, 1)
    return report


def regression_gate(before, after, tolerance=0.0):
    """(ok, drops): drops is a list of (field, before, after) for every field in FIELDS and "all_fields" whose percent
    fell by more than tolerance points; ok is True when nothing fell."""
    drops = [(f, before[f], after[f]) for f in FIELDS + ["all_fields"] if after[f] < before[f] - tolerance]
    return not drops, drops


if __name__ == "__main__":
    golden = load_golden()
    v1 = eval_report(golden, load_run("data/run_v1.json"))
    v2 = eval_report(golden, load_run("data/run_v2.json"))
    print(f"{'field':<16}{'v1':>7}{'v2':>7}")
    for field in FIELDS + ["all_fields"]:
        print(f"{field:<16}{v1[field]:>7}{v2[field]:>7}")
    ok, drops = regression_gate(v1, v2)
    print("gate:", "PASS" if ok else "FAIL", drops)
