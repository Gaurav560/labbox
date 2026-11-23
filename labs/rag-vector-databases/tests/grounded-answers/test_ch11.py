import r

SOURCES = [
    {"id": "FM-5.3", "title": "Fighting a ground fire", "text": "Never fight a crown fire.", "rerank": 4.0},
    {"id": "FM-5.1", "title": "The fire season", "text": "15 February to 31 May.", "rerank": 1.0},
]


def test_grounded_prompt():
    def check():
        import fieldbook as fb
        q = "What should the crew do when the treetops are burning?"
        got = fb.grounded_messages(q, SOURCES)
        if not isinstance(got, list) or len(got) != 2:
            return r.failed("grounded_prompt", "Return two messages: system, then user.")
        if got[0] != {"role": "system", "content": fb.GROUNDED}:
            return r.failed("grounded_prompt", "The system message is GROUNDED: it tells the model to cite by number and to say NOT_FOUND when the sources lack the answer.")
        text = got[1].get("content", "")
        if got[1].get("role") != "user" or not text.startswith("Sources:"):
            return r.failed("grounded_prompt", "The user message starts with \"Sources:\".", "Sources:", text[:20])
        for n, s in enumerate(SOURCES, start=1):
            want = f"[{n}] {s['id']}: {s['title']}\n{s['text']}"
            if want not in text:
                if f"[{n - 1}] {s['id']}" in text:
                    return r.failed("grounded_prompt", "Number the sources from 1 (enumerate(sources, start=1)): people and models count from 1.", want, text[:80])
                return r.failed("grounded_prompt", "Each source as \"[1] FM-5.3: Fighting a ground fire\" on one line, its text on the next.", want, text[:120])
        if not text.rstrip().endswith(f"Question: {q}"):
            return r.failed("grounded_prompt", "End with \"Question: \" and the question.")
        r.passed("grounded_prompt", "Numbered sources: the model can now point at its evidence, and you can check every claim.")
    r.task("grounded_prompt", check)


def test_refuse_unsure(fake):
    def check():
        from openai import OpenAI
        import fieldbook as fb
        client = OpenAI()
        weak = [dict(SOURCES[0], rerank=fb.MIN_RERANK - 1)]
        for sources in ([], weak):
            got = fb.answer("What is the entry fee for a foreign tourist?", sources, client)
            if got != {"answer": fb.NOT_FOUND, "sources": []}:
                return r.failed("refuse_unsure", "With no sources, or a best source below MIN_RERANK, return {\"answer\": NOT_FOUND, \"sources\": []}.",
                                {"answer": fb.NOT_FOUND, "sources": []}, got)
            if fake.chat_requests:
                return r.failed("refuse_unsure", "Do not call the model when the sources are too weak: that is the point (no cost, no invented answer).")
        fake.script = lambda body: "Move the crew to a fire line and wait [1]."
        q = "What should the crew do when the treetops are burning?"
        got = fb.answer(q, SOURCES, client)
        if len(fake.chat_requests) != 1:
            return r.failed("refuse_unsure", "With a good best source, call the model once.", 1, len(fake.chat_requests))
        req = fake.chat_requests[0]
        if req.get("model") != "lab-chat" or req.get("temperature") != 0:
            return r.failed("refuse_unsure", "Use model \"lab-chat\" with temperature 0.", "lab-chat, 0", f"{req.get('model')}, {req.get('temperature')}")
        if req.get("messages") != fb.grounded_messages(q, SOURCES):
            return r.failed("refuse_unsure", "Send grounded_messages(question, sources).")
        if got != {"answer": "Move the crew to a fire line and wait [1].", "sources": ["FM-5.3", "FM-5.1"]}:
            return r.failed("refuse_unsure", "Return the model's text and the ids of the sources, in order.",
                            {"answer": "Move the crew ...", "sources": ["FM-5.3", "FM-5.1"]}, got)
        r.passed("refuse_unsure", "An assistant that knows when it does not know: no source, no answer, and no model call to pay for.")
    r.task("refuse_unsure", check)
