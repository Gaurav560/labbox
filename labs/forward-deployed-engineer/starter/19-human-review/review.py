"""Shadow mode: Claimdesk drafts silently while the adjusters work as usual; compare before anyone relies on it.
Run it with: python review.py"""
import json


def load_shadow(path):
    """Rows of {email_id, kind, claimdesk, reasons, adjuster, adjuster_note}: Claimdesk's draft and the adjuster's
    decision ("pay" or "refer") for the same claim."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def shadow_report(rows):
    """{"cases": n, "agree": how many have the same draft and decision, "agreement": agree / n * 100 rounded to 1 place,
    "unsafe": ids where Claimdesk drafted pay but the adjuster referred, "extra_work": ids where Claimdesk drafted refer
    but the adjuster paid}. Ids in the order of the rows."""
    # TODO (task shadow_report): go through the rows once, sorting each into agree, unsafe or extra_work.
    return {"cases": len(rows), "agree": 0, "agreement": 0.0, "unsafe": [], "extra_work": []}


def go_live_check(report, min_agreement=90.0, min_cases=30):
    """(ok, reasons). Reasons, in this order, each only when it applies:
    "only N cases, need M"; "unsafe drafts: E-02, E-25" (the ids, joined by ", "); "agreement A% is below M%".
    ok is True when there are no reasons."""
    # TODO (task go_live_check): build the reasons list from the three rules, in order.
    return True, []


if __name__ == "__main__":
    for name in ("week1", "week1_replayed"):
        rows = load_shadow(f"data/shadow_{name}.json")
        report = shadow_report(rows)
        print(f"{name}: {report['agree']} of {report['cases']} agree ({report['agreement']}%)")
        by_id = {r["email_id"]: r for r in rows}
        for label in ("unsafe", "extra_work"):
            for eid in report[label]:
                r = by_id[eid]
                print(f"   {label:<10} {eid} {r['kind']:<8} Claimdesk {r['claimdesk']}, adjuster: {r['adjuster_note']}")
        print("   go live?", go_live_check(report))
