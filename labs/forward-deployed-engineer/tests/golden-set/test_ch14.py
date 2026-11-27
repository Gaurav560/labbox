import r


def test_field_match():
    def check():
        from golden import field_match
        cases = [("policy_no", "DS-POL-40000", "DS-POL-40000", True), ("policy_no", " DS-POL-40000 ", "DS-POL-40000", True),
                 ("policy_no", "ds-pol-40592", "DS-POL-40592", False), ("policy_no", "null", None, False),
                 ("policy_no", None, None, True), ("incident_date", None, "2026-10-06", False),
                 ("photos_attached", 1, True, False), ("photos_attached", False, False, True),
                 ("amount_rs", 12500, 12500, True), ("amount_rs", True, 1, False), ("amount_rs", "12500", 12500, False)]
        for field, got, truth, want in cases:
            res = field_match(field, got, truth)
            if res is not want:
                why = {("policy_no", "ds-pol-40592"): "The policy lookup is exact SQL: ds-pol-40592 finds nothing, so it is wrong, not \"nearly right\".",
                       ("policy_no", "null"): "The text \"null\" is not None: the model wrote a word, not an empty field.",
                       ("photos_attached", 1): "A yes/no must be a real bool: 1 is not True here (use is).",
                       ("amount_rs", True): "True is not the number 1 here: refuse bools where an int is expected.",
                       ("amount_rs", "12500"): "The text \"12500\" is not the number 12500."}.get((field, got), "Follow the rules in the docstring, in order.")
                return r.failed("field_match", f"field_match({field!r}, {got!r}, {truth!r}) should be {want}. {why}", want, res)
        r.passed("field_match", "Strict where the next step is strict: a near miss on a policy number is a miss, because the database says so.")
    r.task("field_match", check)


def test_stratified():
    def check():
        from golden import load_golden, stratified
        got = [c["email_id"] for c in stratified(load_golden(), 2)]
        want = ["E-01", "E-02", "E-03", "E-04", "E-05", "E-06", "E-08", "E-10", "E-12", "E-13", "E-14", "E-21"]
        if got != want:
            if got[:2] == ["E-01", "E-02"] and len(got) == 2:
                return r.failed("stratified", "Keep up to per_kind cases of EACH incident_type, not the first per_kind cases overall.", want, got)
            return r.failed("stratified", "Go through the golden set in order, counting per kind, and keep a case while its kind has fewer than per_kind.", want, got)
        one = [c["email_id"] for c in stratified(load_golden(), 1)]
        if len(one) != 6:
            return r.failed("stratified", "With per_kind=1 you should get one case of each of the 6 kinds.", 6, len(one))
        r.passed("stratified", "A small set that still has every kind of claim: fires and floods are rare, and still tested.")
    r.task("stratified", check)
