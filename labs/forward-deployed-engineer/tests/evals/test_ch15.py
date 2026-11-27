import r

GOLD = [{"email_id": "A", "truth": {"policy_no": "DS-POL-1", "vehicle_reg": "X", "incident_date": None, "incident_type": "fire",
                                    "amount_rs": 10, "photos_attached": True}},
        {"email_id": "B", "truth": {"policy_no": "DS-POL-2", "vehicle_reg": "Y", "incident_date": "2026-10-01", "incident_type": "glass",
                                    "amount_rs": 20, "photos_attached": False}}]


def test_eval_report():
    def check():
        from evals import eval_report, load_golden, load_run
        run = {"A": dict(GOLD[0]["truth"]), "B": None}
        rep = eval_report(GOLD, run)
        if rep.get("policy_no") != 50.0 or rep.get("all_fields") != 50.0:
            return r.failed("eval_report", "A is all right and B could not be read: every field is 50.0%, and all_fields 50.0%. An unread email is wrong on every field.",
                            {"policy_no": 50.0, "all_fields": 50.0}, rep)
        run = {"A": {**GOLD[0]["truth"], "amount_rs": 11}, "B": dict(GOLD[1]["truth"])}
        rep = eval_report(GOLD, run)
        if rep.get("amount_rs") != 50.0 or rep.get("vehicle_reg") != 100.0 or rep.get("all_fields") != 50.0:
            return r.failed("eval_report", "One wrong amount: amount_rs 50.0%, the other fields 100.0%, and all_fields 50.0% (A is no longer fully right).",
                            {"amount_rs": 50.0, "vehicle_reg": 100.0, "all_fields": 50.0}, rep)
        v1 = eval_report(load_golden(), load_run("data/run_v1.json"))
        if v1.get("incident_date") != 83.3 or v1.get("all_fields") != 73.3:
            return r.failed("eval_report", "On the real run v1: incident_date 83.3%, all_fields 73.3%. Use field_match for every comparison and round to 1 place.",
                            {"incident_date": 83.3, "all_fields": 73.3}, {k: v1.get(k) for k in ("incident_date", "all_fields")})
        r.passed("eval_report", "Now \"how often is it right?\" has an answer per field, on real cases, that anyone can rerun.")
    r.task("eval_report", check)


def test_regression_gate():
    def check():
        from evals import FIELDS, regression_gate
        base = {f: 90.0 for f in FIELDS + ["all_fields"]}
        ok, drops = regression_gate(base, dict(base))
        if ok is not True or drops != []:
            return r.failed("regression_gate", "Nothing changed: the gate passes with no drops.", (True, []), (ok, drops))
        after = {**base, "incident_date": 86.7, "all_fields": 96.7}
        ok, drops = regression_gate(base, after)
        if ok is not False or drops != [("incident_date", 90.0, 86.7)]:
            return r.failed("regression_gate", "incident_date fell from 90.0 to 86.7: the gate fails and lists it, even though all_fields went up.",
                            (False, [("incident_date", 90.0, 86.7)]), (ok, drops))
        ok, drops = regression_gate(base, after, tolerance=5.0)
        if ok is not True:
            return r.failed("regression_gate", "With tolerance=5.0 a fall of 3.3 points is allowed: compare after < before - tolerance.", True, ok)
        after = {**base, "all_fields": 80.0}
        if regression_gate(base, after)[1] != [("all_fields", 90.0, 80.0)]:
            return r.failed("regression_gate", "Check all_fields too, after the FIELDS.", [("all_fields", 90.0, 80.0)], regression_gate(base, after)[1])
        r.passed("regression_gate", "A change that makes one field worse is stopped, however good the average looks.")
    r.task("regression_gate", check)
