import r


def test_steady_model(fake):
    def check():
        from params import steady_model
        m = steady_model()
        if m is None:
            return r.failed("steady_model", "steady_model() returned None. Return init_chat_model(\"openai:ai-chat\", temperature=0, max_tokens=120).")
        m.invoke("Hello")
        body = fake.chat_requests[-1]
        if body.get("temperature") != 0:
            return r.failed("steady_model", "Send temperature=0.", 0, body.get("temperature"))
        limit = body.get("max_tokens", body.get("max_completion_tokens"))
        if limit != 120:
            return r.failed("steady_model", "Cap the answer with max_tokens=120.", 120, limit)
        r.passed("steady_model", "Temperature 0 for steady answers, and a ceiling on every answer's length and cost.")
    r.task("steady_model", check)


def test_stream_tokens(fake):
    def check():
        from params import SYSTEM, stream_answer, steady_model
        m = steady_model()
        if m is None:
            return r.failed("stream_tokens", "First build the model (the task above).")
        fake.script = lambda b: "Rain spoils stored onions, so supply falls."
        seen = []
        got = stream_answer(m, "Why?", seen.append)
        if not fake.chat_requests or not fake.chat_requests[-1].get("stream"):
            return r.failed("stream_tokens", "Use model.stream([...]), not invoke: the request must ask for a stream.")
        if fake.texts(fake.chat_requests[-1], "system") != [SYSTEM]:
            return r.failed("stream_tokens", "Stream the system message and the question, like chapter 7.")
        if len([p for p in seen if p]) < 3:
            return r.failed("stream_tokens", "Call on_piece(chunk.content) for every chunk, as it arrives.", "several pieces", seen)
        if got != "Rain spoils stored onions, so supply falls.":
            return r.failed("stream_tokens", "Return all the pieces joined together.", "Rain spoils stored onions, so supply falls.", got)
        r.passed("stream_tokens", "Each piece shown the moment it exists: the passenger reads while the model writes.")
    r.task("stream_tokens", check)
