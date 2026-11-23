import json

import r
from fake_openai import Reply


def test_extract_booking(fake):
    def check():
        from booking import Booking, extract_booking
        fake.script = lambda b: Reply(json.dumps({"crop": "onion", "crates": 60, "days": 14}))
        got = extract_booking("60 crates of kanda for two weeks")
        if not isinstance(got, Booking):
            return r.failed("extract_booking", "Return model.with_structured_output(Booking).invoke(message): a Booking, not text.", "Booking", type(got).__name__)
        rf = fake.chat_requests[-1].get("response_format") or {}
        if rf.get("type") != "json_schema":
            return r.failed("extract_booking", "Use with_structured_output(Booking), which sends the Booking schema to the model.")
        if (got.crop, got.crates, got.days) != ("onion", 60, 14):
            return r.failed("extract_booking", "Return the parsed Booking.", "onion, 60, 14", got)
        r.passed("extract_booking", "Free text in, a checked Python object out: the co-op's code can now book it without reading English.")
    r.task("extract_booking", check)


def test_booking_agent(fake):
    def check():
        from booking import Booking, booking_agent
        agent = booking_agent()
        if agent is None:
            return r.failed("booking_agent", "booking_agent() returned None. Return create_agent(\"openai:ai-chat\", tools=[], response_format=Booking).")
        fake.script = lambda b: Reply.tool("Booking", {"crop": "grapes", "crates": 40, "days": 3})
        result = agent.invoke({"messages": [{"role": "user", "content": "40 crates of grapes for 3 days"}]})
        if "Booking" not in fake.tool_names(fake.chat_requests[0]):
            return r.failed("booking_agent", "Pass response_format=Booking: the agent then offers the model a Booking tool to answer with.")
        got = result.get("structured_response")
        if not isinstance(got, Booking) or (got.crop, got.crates, got.days) != ("grapes", 40, 3):
            return r.failed("booking_agent", "The run should end with result[\"structured_response\"], a Booking.", "Booking(grapes, 40, 3)", got)
        r.passed("booking_agent", "An agent whose last step is a typed object: here the model answered by calling a Booking tool.")
    r.task("booking_agent", check)
