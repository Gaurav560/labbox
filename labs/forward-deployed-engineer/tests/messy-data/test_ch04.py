import r
from datetime import date


def test_parse_amount():
    def check():
        from clean import parse_amount
        cases = [("Rs 21,500", 21500), ("₹ 3,37,500", 337500), ("34500.00", 34500), ("36500", 36500), ("  8000 ", 8000),
                 ("Rs 1,23,45,678", 12345678), ("", None), ("   ", None), ("N/A", None)]
        for text, want in cases:
            got = parse_amount(text)
            if got != want:
                why = {"₹ 3,37,500": "Indian amounts put commas after the lakh too (3,37,500): take away every comma, wherever it is.",
                       "34500.00": "\"34500.00\" has paise: read it with float() first, then int().",
                       "": "A blank amount means the branch did not type one: return None, never 0.",
                       "N/A": "Text that is not a number should give None (catch the ValueError), not crash."}.get(text,
                       "Take away \"Rs\", \"₹\" and every comma, strip the spaces, then read the number.")
                return r.failed("parse_amount", f"parse_amount({text!r}) should be {want!r}. {why}", want, got)
            if want is not None and not isinstance(got, int):
                return r.failed("parse_amount", f"parse_amount({text!r}) should be an int (whole rupees), not {type(got).__name__}.", want, got)
        r.passed("parse_amount", "Four ways of writing rupees, one number. A blank stays None: nobody claimed Rs 0.")
    r.task("parse_amount", check)


def test_clean_export():
    def check():
        from clean import clean_export, load_raw
        rows = [
            {"claim_id": "A", "received": "02/07/2026", "amount": "Rs 1,000", "vehicle": "car", "channel": "email"},
            {"claim_id": "A", "received": "02/07/2026", "amount": "Rs 1,000", "vehicle": "car", "channel": "email"},
            {"claim_id": "B", "received": "someday", "amount": "500", "vehicle": "car", "channel": "email"},
            {"claim_id": "C", "received": "2026-07-03", "amount": "", "vehicle": "car", "channel": "email"},
            {"claim_id": "D", "received": "04 Jul 2026", "amount": "700.00", "vehicle": "two-wheeler", "channel": "branch"},
        ]
        clean, rejected = clean_export(rows)
        if rejected != [("A", "duplicate"), ("B", "bad date"), ("C", "no amount")]:
            return r.failed("clean_export", "For a duplicate A, a row with a bad date and one with no amount, rejected should list them "
                            "in order with those reasons (check the date before the amount).",
                            [("A", "duplicate"), ("B", "bad date"), ("C", "no amount")], rejected)
        if [c["claim_id"] for c in clean] != ["A", "D"]:
            return r.failed("clean_export", "Only the first copy of A and the good row D are clean.", ["A", "D"], [c["claim_id"] for c in clean])
        if clean[0]["received"] != date(2026, 7, 2) or clean[0]["amount_rs"] != 1000:
            return r.failed("clean_export", "A clean row has received as a date (parse_date) and amount_rs as an int (parse_amount). "
                            "02/07/2026 is 2 July: Indian dates put the day first.", (date(2026, 7, 2), 1000),
                            (clean[0].get("received"), clean[0].get("amount_rs")))
        clean, rejected = clean_export(load_raw())
        if len(clean) != 238 or len(rejected) != 7:
            return r.failed("clean_export", "On the real export: 245 rows give 238 clean claims and 7 rejected (5 duplicates, 2 with no amount).",
                            (238, 7), (len(clean), len(rejected)))
        r.passed("clean_export", "238 claims you can trust, and 7 rejections with a reason you can send back to the branch IT team.")
    r.task("clean_export", check)
