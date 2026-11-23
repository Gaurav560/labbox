import r
from fake_openai import Reply


def test_aadhaar_detector(fake):
    def check():
        from agent import find_aadhaar, navin_agent
        got = find_aadhaar("Aadhaar 4821 3390 1176 and 482133901176, not 1234 5678 9012 or Rs 50000")
        values = [m.get("value") for m in got]
        if values != ["4821 3390 1176", "482133901176"]:
            return r.failed("aadhaar_detector", "Return one dict per AADHAAR match, with type, value, start and end.",
                            ["4821 3390 1176", "482133901176"], values)
        if got[0] != {"type": "aadhaar", "value": "4821 3390 1176", "start": 8, "end": 22}:
            return r.failed("aadhaar_detector", "Each match is {\"type\": \"aadhaar\", \"value\": m.group(), \"start\": m.start(), \"end\": m.end()}.",
                            {"type": "aadhaar", "value": "4821 3390 1176", "start": 8, "end": 22}, got[0])
        fake.script = lambda b: Reply("ok")
        navin_agent().invoke({"messages": [{"role": "user", "content": "My Aadhaar is 4821 3390 1176."}]})
        sent = " ".join(fake.texts(fake.chat_requests[-1], "user"))
        if "4821" in sent or "3390" in sent:
            return r.failed("aadhaar_detector", "The Aadhaar number still reached the model.", "masked", sent)
        r.passed("aadhaar_detector", f"The model received {sent!r}: the number never left the co-op's server.")
    r.task("aadhaar_detector", check)


def test_length_guard(fake):
    def check():
        from agent import TOO_LONG, navin_agent
        fake.script = lambda b: Reply("ok")
        result = navin_agent().invoke({"messages": [{"role": "user", "content": "x" * 600}]})
        if fake.chat_requests:
            return r.failed("length_guard", "A 600-character message still reached the model. Return {\"messages\": [AIMessage(TOO_LONG)], \"jump_to\": \"end\"} when it is too long.")
        if result["messages"][-1].content != TOO_LONG:
            return r.failed("length_guard", "The member should get TOO_LONG as the answer.", TOO_LONG, result["messages"][-1].content)
        navin_agent().invoke({"messages": [{"role": "user", "content": "short question"}]})
        if not fake.chat_requests:
            return r.failed("length_guard", "Short messages should go through: return None when the message is not too long.")
        r.passed("length_guard", "A long message gets a polite refusal and costs nothing: the model is never called.")
    r.task("length_guard", check)
