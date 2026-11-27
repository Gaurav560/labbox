import r

ROW = {"Claim No": "KC-1", "Policy Ref": " km/26/004519 ", "Vehicle": "mh 04 cd-5678", "Loss Date": "04-11-2026", "Cause": "THF",
       "Estimate": "28,000.00", "Photos": "Y"}


def test_from_konkan():
    def check():
        from product import from_konkan
        want = {"policy_no": "KM/26/004519", "vehicle_reg": "MH04CD5678", "incident_date": "2026-11-04", "incident_type": "theft",
                "amount_rs": 28000, "photos_attached": True}
        got = from_konkan(ROW)
        if got != want:
            diff = [k for k in want if got.get(k) != want[k]]
            return r.failed("from_konkan", f"Wrong: {diff}. Follow the docstring for each column.", want, got)
        empty = from_konkan({**ROW, "Policy Ref": "", "Vehicle": "", "Loss Date": "", "Cause": "VAN", "Estimate": "", "Photos": ""})
        want = {"policy_no": None, "vehicle_reg": None, "incident_date": None, "incident_type": "other", "amount_rs": None, "photos_attached": False}
        if empty != want:
            return r.failed("from_konkan", "Empty columns become None (photos: False), and an unknown cause code is \"other\".", want, empty)
        if from_konkan({**ROW, "Estimate": "4,999.60"})["amount_rs"] != 5000:
            return r.failed("from_konkan", "Round the estimate to whole rupees: 4,999.60 is 5000.", 5000, from_konkan({**ROW, "Estimate": "4,999.60"})["amount_rs"])
        if type(from_konkan(ROW)["amount_rs"]) is not int:
            return r.failed("from_konkan", "amount_rs must be an int, like the model's answer for Deccan Shield.")
        r.passed("from_konkan", "Konkan's CSV now looks exactly like what the model reads from Deccan Shield's emails. Everything after it is shared.")
    r.task("from_konkan", check)


def test_customer_rules():
    def check():
        from product import DECCAN, KONKAN, rules
        pol = {"vehicle_reg": "MH04CD5678", "start_date": "2026-04-01", "end_date": "2027-03-31"}
        f = {"policy_no": "KM/26/004519", "vehicle_reg": "MH04CD5678", "incident_date": "2026-11-04", "incident_type": "accident",
             "amount_rs": 12000, "photos_attached": True}
        if rules(f, pol, KONKAN) != []:
            return r.failed("customer_rules", "A clean claim has no reasons.", [], rules(f, pol, KONKAN))
        cases = [
            ({**f, "amount_rs": 31000}, pol, KONKAN, ["above the pilot limit"]),
            ({**f, "amount_rs": 31000}, {**pol}, {**DECCAN, "policy_pattern": r"KM/\d{2}/\d{6}"}, []),
            ({**f, "incident_type": "fire"}, pol, KONKAN, ["fire: always referred"]),
            ({**f, "incident_type": "fire"}, pol, DECCAN | {"policy_pattern": r"KM/\d{2}/\d{6}"}, []),
            ({**f, "policy_no": "KM/26/04577"}, None, KONKAN, ["policy number not in the expected format"]),
            ({**f, "policy_no": None, "amount_rs": None}, None, KONKAN, ["no policy number", "no amount"]),
            (f, None, KONKAN, ["unknown policy"]),
            ({**f, "vehicle_reg": "MH04ST1122", "incident_date": "2026-03-01", "amount_rs": 40000, "incident_type": "theft"}, pol, KONKAN,
             ["registration does not match the policy", "incident outside the policy period", "above the pilot limit", "theft: always referred"]),
        ]
        for fields, policy, config, want in cases:
            got = rules(fields, policy, config)
            if got != want:
                return r.failed("customer_rules", "Take the limit, the always-refer kinds and the policy pattern from config, and keep the order "
                                "in the docstring.", want, got)
        r.passed("customer_rules", "One rules function, two customers, the differences in config. That is a product.")
    r.task("customer_rules", check)
