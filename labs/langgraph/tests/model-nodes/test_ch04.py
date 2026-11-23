import json

import r
from fake_openai import Reply


def test_triage_node(fake):
    def check():
        from graph import TRIAGE, triage
        fake.script = lambda b: Reply(json.dumps({"kind": "dirty_water", "severity": "urgent", "street": "Tilak Nagar"}))
        got = triage({"text": "Water smells in Tilak Nagar"})
        if got != {"kind": "dirty_water", "severity": "urgent", "street": "Tilak Nagar"}:
            return r.failed("triage_node", "Return the Triage as a dict: model().with_structured_output(Triage).invoke([...]).model_dump().",
                            {"kind": "dirty_water", "severity": "urgent", "street": "Tilak Nagar"}, got)
        body = fake.chat_requests[-1]
        if fake.texts(body, "system") != [TRIAGE] or fake.texts(body, "user") != ["Water smells in Tilak Nagar"]:
            return r.failed("triage_node", "Send SystemMessage(TRIAGE) and the complaint as a HumanMessage.")
        if (body.get("response_format") or {}).get("type") != "json_schema":
            return r.failed("triage_node", "Use with_structured_output(Triage), so the answer is checked against the schema.")
        r.passed("triage_node", "A node that calls a model is still just a function: state in, an update out.")
    r.task("triage_node", check)


def test_reply_node(fake):
    def check():
        from graph import REPLY, draft_reply
        fake.script = lambda b: Reply("We have received your complaint and will respond within 4 hours.")
        got = draft_reply({"text": "Smell", "kind": "dirty_water", "severity": "urgent", "street": "Tilak Nagar"})
        if got != {"reply": "We have received your complaint and will respond within 4 hours."}:
            return r.failed("reply_node", "Return {\"reply\": <the model's answer content>}.", "the model's text", got)
        user = " ".join(fake.texts(fake.chat_requests[-1], "user"))
        if "within 4 hours" not in user or fake.texts(fake.chat_requests[-1], "system") != [REPLY]:
            return r.failed("reply_node", "Send SystemMessage(REPLY) and the facts (with the response time) as the HumanMessage.")
        r.passed("reply_node", "The reply promises only the time Python computed from the severity.")
    r.task("reply_node", check)
