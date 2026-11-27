import r


def test_classify_failure():
    def check():
        from failures import classify_failure
        cases = [("amount_rs", None, 12500, "missing"), ("incident_date", "2026-10-30", None, "invented"),
                 ("policy_no", "null", None, "invented"), ("policy_no", "ds-pol-40592", "DS-POL-40592", "format"),
                 ("policy_no", "DS POL 40999", "DS-POL-40999", "format"), ("incident_date", "2023-10-06", "2026-10-06", "wrong"),
                 ("incident_type", "accident", "other", "wrong")]
        for field, got, truth, want in cases:
            res = classify_failure(field, got, truth)
            if res != want:
                return r.failed("classify_failure", f"classify_failure({field!r}, {got!r}, {truth!r}) should be {want!r}. Test missing, then invented, "
                                "then format (squash both), then wrong.", want, res)
        r.passed("classify_failure", "Nine wrong fields became four kinds of problem. Kinds can be fixed; cases can only be patched.")
    r.task("classify_failure", check)


def test_fix_fields():
    def check():
        from failures import fix_fields
        src = {"policy_no": "ds pol-40999", "vehicle_reg": "MH12AB1234", "incident_date": "2023-10-06", "incident_type": "accident",
               "amount_rs": 100, "photos_attached": True}
        got = fix_fields(src)
        if got.get("policy_no") != "DS-POL-40999":
            return r.failed("fix_fields", "A policy number that squashes to DSPOL and five digits is rebuilt as DS-POL-40999.", "DS-POL-40999", got.get("policy_no"))
        if got.get("incident_date") != "2026-10-06":
            return r.failed("fix_fields", "2023-10-06 is in an earlier year than today (2026-10-31): give it this year, 2026-10-06.", "2026-10-06", got.get("incident_date"))
        if src["policy_no"] != "ds pol-40999":
            return r.failed("fix_fields", "Return a new dict and leave the input unchanged (dict(fields) makes a copy).")
        late = fix_fields({**src, "incident_date": "2023-12-20"})
        if late.get("incident_date") != "2025-12-20":
            return r.failed("fix_fields", "20 December in this year would be after today (31 October): use the year before.", "2025-12-20", late.get("incident_date"))
        if fix_fields({**src, "policy_no": "null"}).get("policy_no") is not None or fix_fields({**src, "policy_no": "NULL"}).get("policy_no") is not None:
            return r.failed("fix_fields", "The text \"null\" (any case) becomes None.", None, fix_fields({**src, "policy_no": "null"}).get("policy_no"))
        same = fix_fields({**src, "incident_date": "2026-10-06", "policy_no": "DS-POL-40000"})
        if same.get("incident_date") != "2026-10-06" or same.get("policy_no") != "DS-POL-40000":
            return r.failed("fix_fields", "Right values must stay as they are.")
        from evals import eval_report, load_golden, load_run
        run = load_run("data/run_v1.json")
        after = eval_report(load_golden(), {k: fix_fields(v) for k, v in run.items()})
        if after.get("all_fields") != 93.3:
            return r.failed("fix_fields", "On the real run v1, the fixes should lift all_fields from 73.3% to 93.3%.", 93.3, after.get("all_fields"))
        r.passed("fix_fields", "73.3% to 93.3% of emails fully right, with code you can test, instead of a prompt you hope works.")
    r.task("fix_fields", check)
