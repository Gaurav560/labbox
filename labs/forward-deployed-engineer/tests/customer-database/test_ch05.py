import r


def test_policy_for_claim():
    def check():
        from db import connect, policy_for_claim
        con = connect()
        got = policy_for_claim(con, "DS-26-10038")
        if not isinstance(got, dict) or got.get("policy_no") != "DS-POL-40000" or got.get("holder") != "M. Joshi":
            return r.failed("policy_for_claim", "Claim DS-26-10038 belongs to policy DS-POL-40000 (holder M. Joshi). JOIN claims to policies "
                            "ON policy_no, WHERE c.claim_id = ?, and return dict(row).", "DS-POL-40000, M. Joshi", got)
        if got.get("sum_insured") != 90000:
            return r.failed("policy_for_claim", "Return every column of the policy (SELECT p.*), with sum_insured as the number 90000.",
                            90000, got.get("sum_insured"))
        if policy_for_claim(con, "DS-26-99999") is not None:
            return r.failed("policy_for_claim", "An unknown claim has no policy: fetchone() gives None, and so should the function.",
                            None, policy_for_claim(con, "DS-26-99999"))
        sneaky = policy_for_claim(con, "DS-26-99999' OR '1'='1")
        if sneaky is not None:
            return r.failed("policy_for_claim", "A claim id written as DS-26-99999' OR '1'='1 returned a policy: the id was pasted into the "
                            "SQL text, so it became SQL. Pass it as a parameter: execute(\"... WHERE c.claim_id = ?\", (claim_id,)).",
                            None, sneaky)
        r.passed("policy_for_claim", "A parameter is always data, never SQL: the sneaky id found nothing, as it should.")
    r.task("policy_for_claim", check)


def test_lapsed_claims():
    def check():
        from db import connect, lapsed_claims
        got = lapsed_claims(connect())
        want = [("DS-26-10088", "2026-09-08", "2026-09-20"), ("DS-26-10100", "2026-06-14", "2026-08-07"),
                ("DS-26-10120", "2026-08-19", "2026-09-07"), ("DS-26-10210", "2026-06-16", "2026-07-06"),
                ("DS-26-10220", "2026-06-18", "2026-07-20"), ("DS-26-10222", "2026-07-12", "2026-08-24")]
        if got != want:
            if isinstance(got, list) and len(got) > 6:
                return r.failed("lapsed_claims", "Too many rows: compare only the date part, substr(c.received_at, 1, 10), with p.end_date. "
                                "The full text \"2026-09-08 10:00\" is always later than \"2026-09-08\".", len(want), len(got))
            return r.failed("lapsed_claims", "Six claims arrived after their policy had ended. Return (claim_id, end_date, received_day) "
                            "tuples, ORDER BY c.claim_id.", want, got)
        r.passed("lapsed_claims", "Six claims on lapsed policies, found in one query. A human must see these before any money moves.")
    r.task("lapsed_claims", check)
