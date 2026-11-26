import r


def claim(vehicle="two-wheeler", channel="email", amount="20000", cid="X"):
    return {"claim_id": cid, "vehicle": vehicle, "channel": channel, "amount_rs": amount}


def test_pilot_slice():
    def check():
        from scope import load_claims, pilot_slice
        cases = [claim(cid="in"), claim(amount="50000", cid="edge"), claim(amount="50500", cid="big"),
                 claim(vehicle="car", cid="car"), claim(channel="branch", cid="branch")]
        got = [c["claim_id"] for c in pilot_slice(cases)]
        if got != ["in", "edge"]:
            if "edge" not in got:
                return r.failed("pilot_slice", "A Rs 50,000 claim is in the pilot (\"or less\"): use <= 50000, and turn amount_rs into an "
                                "int first (it is a string in the CSV).", ["in", "edge"], got)
            return r.failed("pilot_slice", "Keep a claim only when all three hold: a two-wheeler, sent by email, for Rs 50,000 or less.",
                            ["in", "edge"], got)
        n = len(pilot_slice(load_claims()))
        if n != 57:
            return r.failed("pilot_slice", "On the real export the pilot should hold 57 claims.", 57, n)
        r.passed("pilot_slice", "57 of 240 claims: small enough to finish in weeks, real enough to matter. That is a pilot.")
    r.task("pilot_slice", check)


def test_measurable_goal():
    def check():
        from scope import GOAL, missing_parts
        if missing_parts(GOAL) != []:
            return r.failed("measurable_goal", "The pilot's GOAL has all five parts, so nothing is missing.", [], missing_parts(GOAL))
        vague = missing_parts({"metric": "make claims faster"})
        if vague != ["baseline", "target", "unit", "by"]:
            return r.failed("measurable_goal", "\"Make claims faster\" has a metric and nothing else. List each absent part, in the order of "
                            "PARTS.", ["baseline", "target", "unit", "by"], vague)
        words = missing_parts({"metric": "m", "baseline": "about 12", "target": "much less", "unit": "days", "by": "2026-12-31"})
        if words != ["baseline", "target"]:
            return r.failed("measurable_goal", "A baseline of \"about 12\" is words, not a number: baseline and target must be int or float "
                            "(isinstance(value, (int, float))).", ["baseline", "target"], words)
        empty = missing_parts({"metric": "", "baseline": 0, "target": 5, "unit": "days", "by": "2026-12-31"})
        if empty != ["metric"]:
            return r.failed("measurable_goal", "An empty metric is missing; a baseline of 0 is a real number and is not missing.",
                            ["metric"], empty)
        r.passed("measurable_goal", "A goal with a metric, a baseline, a target, a unit and a date can be won or lost. Anything else is a wish.")
    r.task("measurable_goal", check)
