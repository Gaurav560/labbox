import r


def row(eid, c, a):
    return {"email_id": eid, "kind": "accident", "claimdesk": c, "reasons": [], "adjuster": a, "adjuster_note": ""}


def test_shadow_report():
    def check():
        from review import load_shadow, shadow_report
        rows = [row("A", "pay", "pay"), row("B", "pay", "refer"), row("C", "refer", "pay"), row("D", "refer", "refer"), row("E", "pay", "refer")]
        got = shadow_report(rows)
        want = {"cases": 5, "agree": 2, "agreement": 40.0, "unsafe": ["B", "E"], "extra_work": ["C"]}
        if got != want:
            return r.failed("shadow_report", "pay/refer is unsafe (Claimdesk would pay what a person stopped), refer/pay is extra work, "
                            "the same on both sides is agreement.", want, got)
        real = shadow_report(load_shadow("data/shadow_week1.json"))
        if real.get("unsafe") != ["E-02", "E-25", "E-30"] or real.get("agreement") != 83.3:
            return r.failed("shadow_report", "On week 1: unsafe E-02, E-25, E-30 and agreement 83.3%.", ["E-02", "E-25", "E-30"], real.get("unsafe"))
        r.passed("shadow_report", "Two kinds of disagreement, kept apart: one costs an adjuster a minute, the other costs money.")
    r.task("shadow_report", check)


def test_go_live_check():
    def check():
        from review import go_live_check
        good = {"cases": 30, "agree": 28, "agreement": 93.3, "unsafe": [], "extra_work": ["E-15", "E-19"]}
        if go_live_check(good) != (True, []):
            return r.failed("go_live_check", "30 cases, nothing unsafe, 93.3% agreement: ready.", (True, []), go_live_check(good))
        bad = {"cases": 12, "agree": 9, "agreement": 75.0, "unsafe": ["E-02", "E-25"], "extra_work": ["E-15"]}
        want = (False, ["only 12 cases, need 30", "unsafe drafts: E-02, E-25", "agreement 75.0% is below 90.0%"])
        if go_live_check(bad) != want:
            return r.failed("go_live_check", "Check the three rules in order and use the reason texts from the docstring.", want, go_live_check(bad))
        one = {"cases": 40, "agree": 39, "agreement": 97.5, "unsafe": ["E-30"], "extra_work": []}
        if go_live_check(one) != (False, ["unsafe drafts: E-30"]):
            return r.failed("go_live_check", "One unsafe draft is enough to stop, however high the agreement.",
                            (False, ["unsafe drafts: E-30"]), go_live_check(one))
        if go_live_check({**good, "agreement": 89.9}, min_agreement=85.0)[0] is not True:
            return r.failed("go_live_check", "Use the min_agreement you are given.")
        r.passed("go_live_check", "Going live is a checklist with numbers, agreed in advance, not a feeling after a good week.")
    r.task("go_live_check", check)
