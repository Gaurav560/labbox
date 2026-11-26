import r

GOOD = {"claim_id": "DS-26-10501", "policy_no": "DS-POL-40000", "vehicle": "two-wheeler", "amount_rs": "12500",
        "received": "2026-10-02", "vehicle_reg": "MH12AB1234"}


def rejects(Claim, ValidationError, **change):
    try:
        Claim(**{**GOOD, **change})
        return False
    except ValidationError:
        return True


def test_claim_model():
    def check():
        from datetime import date
        from contract import Claim
        from pydantic import ValidationError
        c = Claim(**GOOD)
        if getattr(c, "amount_rs", None) != 12500 or getattr(c, "received", None) != date(2026, 10, 2):
            return r.failed("claim_model", "A good row should become a Claim with amount_rs the int 12500 and received the date 2 October "
                            "2026: declare amount_rs: int and received: date.", "12500, 2026-10-02",
                            f"{getattr(c, 'amount_rs', None)!r}, {getattr(c, 'received', None)!r}")
        bad = [("vehicle", "bike", "vehicle must be one of the three kinds: Literal[\"two-wheeler\", \"car\", \"commercial\"]"),
               ("amount_rs", "0", "an amount of 0 is not a claim: Field(gt=0)"),
               ("policy_no", "", "an empty policy number must be rejected: pattern ^DS-POL-\\d{5}$"),
               ("claim_id", "10508", "a claim id without DS-26- is not ours: pattern ^DS-26-\\d{5}$"),
               ("received", "2026-09-31", "31 September does not exist: declare received: date"),
               ("vehicle_reg", "KA01MN", "KA01MN has no number at the end: check it against REG")]
        for field, value, why in bad:
            if not rejects(Claim, ValidationError, **{field: value}):
                return r.failed("claim_model", f"{field}={value!r} was accepted. {why}.", "ValidationError", "accepted")
        reg = Claim(**{**GOOD, "vehicle_reg": "mh-12 ab 9876"}).vehicle_reg
        if reg != "MH12AB9876":
            return r.failed("claim_model", "Registrations arrive as \"mh-12 ab 9876\": the field_validator should upper-case them and remove "
                            "spaces and dashes before checking, and return the clean value.", "MH12AB9876", reg)
        r.passed("claim_model", "The contract is code now: every claim is the same shape, or it is refused with a reason.")
    r.task("claim_model", check)


def test_contract_report():
    def check():
        from contract import contract_report, load_incoming
        valid, errors = contract_report(load_incoming())
        if len(valid) != 5:
            return r.failed("contract_report", "5 of the 12 incoming rows keep the contract.", 5, len(valid))
        rows = [e[0] for e in errors]
        if rows != [3, 4, 5, 6, 8, 9, 10]:
            if rows and rows[0] == 2:
                return r.failed("contract_report", "Number the rows from 1: enumerate(rows, start=1).", [3, 4, 5, 6, 8, 9, 10], rows)
            return r.failed("contract_report", "Each rejected row should appear with its number, once per problem.", [3, 4, 5, 6, 8, 9, 10], rows)
        fields = [e[1] for e in errors]
        if fields != ["vehicle", "amount_rs", "policy_no", "received", "claim_id", "amount_rs", "vehicle_reg"]:
            return r.failed("contract_report", "The field is the first part of err[\"loc\"], as a string.",
                            ["vehicle", "amount_rs", "policy_no", "received", "claim_id", "amount_rs", "vehicle_reg"], fields)
        if not all(isinstance(e[2], str) and e[2] for e in errors):
            return r.failed("contract_report", "Each error needs pydantic's message, err[\"msg\"].", "messages", errors)
        r.passed("contract_report", "Seven rows, seven reasons, by row and field: a report the customer's IT team can fix things from.")
    r.task("contract_report", check)
