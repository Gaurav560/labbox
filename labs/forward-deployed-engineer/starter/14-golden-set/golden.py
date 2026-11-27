"""The golden set: the cases every version of Claimdesk is measured on. Run it with: python golden.py"""
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
    # TODO (task field_match): truth None -> right only if got is None. got None (truth known) -> wrong. A bool truth ->
    # got is truth (1 is not True here). A str truth -> got is a str and got.strip() == truth. Otherwise (ints) -> got is
    # an int, not a bool, and equal.
    return got == truth


def stratified(golden, per_kind):
    """Up to per_kind cases of each incident_type (from the truth), keeping the golden set's order."""
    # TODO (task stratified): count how many of each kind you have kept so far (a dict); keep a case while its kind's
    # count is below per_kind.
    return golden[:per_kind]


if __name__ == "__main__":
    golden = load_golden()
    kinds = {}
    for case in golden:
        kinds[case["truth"]["incident_type"]] = kinds.get(case["truth"]["incident_type"], 0) + 1
    print(f"{len(golden)} cases:", kinds)
    nulls = sum(1 for c in golden for f in FIELDS if c["truth"][f] is None)
    print(f"fields the adjusters left empty (the email did not say): {nulls}")
    print("two of each kind:", [c["email_id"] for c in stratified(golden, 2)])
    for field, got, truth in [("policy_no", "ds-pol-40592", "DS-POL-40592"), ("policy_no", "null", None),
                              ("incident_date", None, None), ("photos_attached", 1, True), ("amount_rs", 12500, 12500)]:
        print(f"  field_match({field!r}, {got!r}, {truth!r}) = {field_match(field, got, truth)}")
