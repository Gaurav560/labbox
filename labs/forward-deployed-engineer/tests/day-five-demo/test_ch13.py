import json

import r
from fake_openai import Reply

EMAIL = "Dear Sir, my Activa MH12AB1234 was hit near Swargate on 3 October 2026. Policy DS-POL-40000. Estimate Rs 12,500."


def fields(**change):
    base = {"policy_no": "DS-POL-40000", "vehicle_reg": "MH12AB1234", "incident_date": "2026-10-03", "incident_type": "accident",
            "amount_rs": 12500, "photos_attached": True}
    return json.dumps({**base, **change})


def post(client, fake, answer, email=EMAIL):
    fake.script = lambda b: Reply(answer)
    return client.post("/triage", json={"email": email})


def test_triage_endpoint(fake):
    def check():
        from fastapi.testclient import TestClient
        from app import app
        c = TestClient(app)
        res = post(c, fake, fields()).json()
        if res.get("draft") != "pay" or res.get("reasons") != []:
            return r.failed("triage_endpoint", "A clean claim (policy in force, registration matching, Rs 12,500) should be drafted \"pay\" with no reasons.",
                            {"draft": "pay", "reasons": []}, res)
        cases = [(fields(amount_rs=61000, vehicle_reg="MH14HJ5656"), ["registration does not match the policy", "above the pilot limit"]),
                 (fields(policy_no="DS-POL-40925", vehicle_reg="MH12LL6767", incident_date="2026-10-26"), ["incident outside the policy period"]),
                 (fields(policy_no=None, amount_rs=None), ["no policy number", "no amount"]),
                 (fields(policy_no="DS-POL-99999"), ["unknown policy"])]
        for answer, want in cases:
            got = post(c, fake, answer).json()
            if got.get("draft") != "refer" or got.get("reasons") != want:
                return r.failed("triage_endpoint", f"These fields should be referred with the reasons {want}, in the TODO's order.",
                                {"draft": "refer", "reasons": want}, {k: got.get(k) for k in ("draft", "reasons")})
        got = post(c, fake, "I cannot read this.").json()
        if got.get("draft") != "refer" or not str((got.get("reasons") or [""])[0]).startswith("could not read the email"):
            return r.failed("triage_endpoint", "When safe_extract cannot read the email, refer it: {\"draft\": \"refer\", \"reasons\": [\"could not read the email: ...\"]}.",
                            "refer, could not read the email", got)
        r.passed("triage_endpoint", "A working demo on real cases: it pays the clean claim and refers every doubtful one, saying why.")
    r.task("triage_endpoint", check)


def test_input_guard(fake):
    def check():
        from fastapi.testclient import TestClient
        from app import app
        c = TestClient(app)
        for email, why in (("", "an empty email"), ("help", "a one-word email"), ("x" * 8001, "an 8,001-character paste")):
            fake.reset()
            res = post(c, fake, fields(), email)
            if res.status_code != 422:
                return r.failed("input_guard", f"{why} reached the endpoint (status {res.status_code}). Give TriageIn.email Field(min_length=20, max_length=8000).",
                                422, res.status_code)
            if fake.chat_requests:
                return r.failed("input_guard", f"{why} was sent to the model. The limits must stop it before any model call.")
        if post(c, fake, fields(), "x" * 8000).status_code != 200:
            return r.failed("input_guard", "An email of exactly 8000 characters is allowed (max_length=8000).", 200, post(c, fake, fields(), "x" * 8000).status_code)
        r.passed("input_guard", "Junk and giant pastes are refused at the door, for free, before a single token is spent.")
    r.task("input_guard", check)
