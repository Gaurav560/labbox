"""Failure analysis: sort every wrong field into a kind, so you fix causes, not cases. Run it with: python failures.py"""
import re
from collections import Counter
from datetime import date

from evals import FIELDS, eval_report, field_match, load_golden, load_run


def squash(text):
    """Text without spaces or dashes, in capitals: "ds pol-40999" -> "DSPOL40999"."""
    return re.sub(r"[\s-]", "", str(text)).upper()


def classify_failure(field, got, truth):
    """For a field that is wrong: "missing" (nothing read, the truth has a value), "invented" (the truth is None but
    something was read), "format" (the same once spaces, dashes and case are ignored), otherwise "wrong"."""
    # TODO (task classify_failure): test in that order: got is None -> "missing"; truth is None -> "invented";
    # squash(got) == squash(truth) -> "format"; else "wrong".
    return "wrong"


def fix_fields(fields, today="2026-10-31"):
    """The fixes the analysis points to, done in code: the text "null" becomes None; a policy number that squashes to
    DSPOL and five digits is written DS-POL-12345; a date in an earlier year than today's gets today's year (or the year
    before, when that would be after today). Returns a new dict; the input is not changed."""
    # TODO (task fix_fields): copy the dict. For every str value equal to "null" (any case) use None. For policy_no,
    # if squash(value) matches ^DSPOL\d{5}$, rebuild it. For incident_date, date.fromisoformat(value); if its year is
    # before date.fromisoformat(today).year, replace the year (and use the year before if the result is after today).
    return dict(fields)


def failure_table(golden, run):
    """Counter of (field, kind) for every wrong field, and one example email for each."""
    table, examples = Counter(), {}
    for case in golden:
        got = run.get(case["email_id"]) or {f: None for f in FIELDS}
        for f in FIELDS:
            if not field_match(f, got[f], case["truth"][f]):
                key = (f, classify_failure(f, got[f], case["truth"][f]))
                table[key] += 1
                examples.setdefault(key, f"{case['email_id']}: got {got[f]!r}, truth {case['truth'][f]!r}")
    return table, examples


if __name__ == "__main__":
    golden = load_golden()
    for name in ("v1", "v2"):
        table, examples = failure_table(golden, load_run(f"data/run_{name}.json"))
        print(f"run {name}: {sum(table.values())} wrong fields")
        for (field, kind), n in table.most_common():
            print(f"   {n} x {field:<15} {kind:<9} e.g. {examples[(field, kind)]}")
    run = load_run("data/run_v1.json")
    fixed = {k: (fix_fields(v) if v else v) for k, v in run.items()}
    before, after = eval_report(golden, run), eval_report(golden, fixed)
    print("v1 before and after the code fixes:")
    for field in FIELDS + ["all_fields"]:
        print(f"   {field:<16}{before[field]:>7}{after[field]:>7}")
