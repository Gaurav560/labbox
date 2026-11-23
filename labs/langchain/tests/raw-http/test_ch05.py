import r


def test_send_request(fake):
    def check():
        from http_call import SYSTEM, ask
        fake.script = lambda b: "The office is open 9 to 5."
        ask("When is the office open?")
        if not fake.chat_requests:
            return r.failed("send_request", "ask(...) never called the model. POST the JSON body to url with httpx.post(...).")
        body, headers = fake.chat_requests[-1], fake.headers[-1]
        if headers.get("authorization") != "Bearer check-key":
            return r.failed("send_request", "Send the key in the Authorization header, as \"Bearer \" plus the key.", "Bearer check-key", headers.get("authorization"))
        if body.get("model") != "ai-chat":
            return r.failed("send_request", "The body needs \"model\": \"ai-chat\".", "ai-chat", body.get("model"))
        roles = [m.get("role") for m in body.get("messages", [])]
        if roles != ["system", "user"] or body["messages"][0]["content"] != SYSTEM or body["messages"][1]["content"] != "When is the office open?":
            return r.failed("send_request", "Send two messages: the system message (SYSTEM), then the user's question.", "['system', 'user']", roles)
        r.passed("send_request", "One HTTP POST with JSON: that is all a chat model API is.")
    r.task("send_request", check)


def test_read_answer(fake):
    def check():
        from http_call import ask
        fake.script = lambda b: "The office is open 9 to 5."
        got = ask("When is the office open?")
        if not fake.chat_requests:
            return r.failed("read_answer", "First send the request (the task above).")
        if got != "The office is open 9 to 5.":
            return r.failed("read_answer", "Return reply[\"choices\"][0][\"message\"][\"content\"].", "The office is open 9 to 5.", got)
        r.passed("read_answer", "JSON in, JSON out, and the answer is one path inside it.")
    r.task("read_answer", check)
