import json

import r
from fake_openai import Reply

FIELDS = {"policy_no": "DS-POL-40000", "vehicle_reg": "MH12AB1234", "incident_date": "2026-10-03", "incident_type": "accident",
          "amount_rs": 12500, "photos_attached": True}


def test_extract_claim(fake):
    def check():
        import extract
        fake.script = lambda b: Reply(json.dumps(FIELDS))
        got = extract.extract_claim("My Activa MH12AB1234 was hit on 3 October 2026. Policy DS-POL-40000. Rs 12,500. Photos attached.")
        if not fake.chat_requests:
            return r.failed("extract_claim", "extract_claim did not call the model.")
        req = fake.chat_requests[-1]
        rf = req.get("response_format") or {}
        if rf.get("type") != "json_schema" or not (rf.get("json_schema") or {}).get("strict"):
            return r.failed("extract_claim", "Send response_format=RESPONSE_FORMAT: a strict JSON schema, so the model must answer with exactly these fields.",
                            "json_schema, strict", rf)
        if fake.texts(req, "system") != [extract.SYSTEM] or not fake.texts(req, "user"):
            return r.failed("extract_claim", "SYSTEM is the system message and the email text the user message.")
        if not isinstance(got, extract.ClaimFields) or got.amount_rs != 12500 or got.policy_no != "DS-POL-40000":
            return r.failed("extract_claim", "Return ClaimFields.model_validate_json(message.content): an object, not the JSON text.",
                            "ClaimFields(amount_rs=12500, ...)", got)
        r.passed("extract_claim", "A free-form email in, six typed fields out, checked against the same model the schema came from.")
    r.task("extract_claim", check)


def test_safe_extract(fake):
    def check():
        import extract
        from openai import OpenAI
        fake.script = lambda b: Reply(json.dumps(FIELDS))
        fields, problem = extract.safe_extract("A claim email, long enough to read.")
        if problem is not None or fields is None:
            return r.failed("safe_extract", "When the model answers well, return (fields, None).", "(fields, None)", (fields, problem))
        fake.script = lambda b: Reply("Sorry, I cannot help with that.")
        fields, problem = extract.safe_extract("A claim email, long enough to read.")
        if fields is not None or problem != "the answer did not match the claim fields":
            return r.failed("safe_extract", "An answer that is not the claim JSON raises ValidationError: catch it and return (None, \"the answer did not match the claim fields\").",
                            (None, "the answer did not match the claim fields"), (fields, problem))
        fake.script = lambda b: Reply(json.dumps({k: v for k, v in FIELDS.items() if k != "amount_rs"}))
        fields, problem = extract.safe_extract("A claim email, long enough to read.")
        if fields is not None:
            return r.failed("safe_extract", "A JSON answer missing a field must not pass: the same ValidationError, the same reason.", None, fields)
        broken = OpenAI(base_url="http://127.0.0.1:9/v1", api_key="x", max_retries=0, timeout=2)
        fields, problem = extract.safe_extract("A claim email, long enough to read.", broken)
        if fields is not None or not str(problem).startswith("the model call failed: "):
            return r.failed("safe_extract", "When the gateway cannot be reached, return (None, \"the model call failed: <the error's class name>\") instead of raising.",
                            "(None, 'the model call failed: APIConnectionError')", (fields, problem))
        r.passed("safe_extract", "One unreadable email can no longer stop a batch of five hundred: it is set aside with its reason.")
    r.task("safe_extract", check)
