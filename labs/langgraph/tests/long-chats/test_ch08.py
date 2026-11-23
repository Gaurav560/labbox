import r
from fake_openai import Reply


def _chat(n):
    from langchain.messages import AIMessage, HumanMessage
    out = []
    for i in range(n):
        out += [HumanMessage(f"citizen {i}", id=f"h{i}"), AIMessage(f"harsh {i}", id=f"a{i}")]
    return out


def test_trim_history(fake):
    def check():
        from chat import KEEP, recent, build_trimmed
        got = [m.content for m in recent(_chat(5))]
        if got != ["citizen 3", "harsh 3", "citizen 4", "harsh 4"]:
            return r.failed("trim_history", "Keep the last KEEP messages, starting with a citizen's message: trim_messages(messages, "
                            "strategy=\"last\", token_counter=len, max_tokens=KEEP, start_on=\"human\").",
                            ["citizen 3", "harsh 3", "citizen 4", "harsh 4"], got)
        fake.script = lambda b: Reply("ok")
        app = build_trimmed()
        config = {"configurable": {"thread_id": "t"}}
        for i in range(5):
            app.invoke({"messages": [("user", f"message {i}")]}, config)
        sent = [m for m in fake.chat_requests[-1]["messages"] if m["role"] != "system"]
        if len(sent) > KEEP:
            return r.failed("trim_history", "respond_trimmed should send only recent(...) to the model.", f"at most {KEEP} messages", len(sent))
        r.passed("trim_history", "The state keeps everything; the model sees only the last few messages.")
    r.task("trim_history", check)


def test_summarise_old(fake):
    def check():
        from langchain.messages import RemoveMessage
        from chat import summarise
        fake.script = lambda b: Reply("Sunita Pawar, 14 Tilak Nagar lane 3, no water since Monday.")
        update = summarise({"messages": _chat(4), "summary": "an earlier summary"})
        if update.get("summary") != "Sunita Pawar, 14 Tilak Nagar lane 3, no water since Monday.":
            return r.failed("summarise_old", "Return {\"summary\": <the model's answer>, ...}.", "the model's summary", update.get("summary"))
        removed = [m.id for m in update.get("messages", []) if isinstance(m, RemoveMessage)]
        if removed != ["h0", "a0", "h1", "a1", "h2", "a2"]:
            return r.failed("summarise_old", "Remove every message except the last two: [RemoveMessage(id=m.id) for m in old].",
                            ["h0", "a0", "h1", "a1", "h2", "a2"], removed)
        body = fake.chat_requests[-1]
        if "an earlier summary" not in " ".join(fake.texts(body, "system")) or "citizen 0" not in " ".join(fake.texts(body, "user")):
            return r.failed("summarise_old", "Send SystemMessage(prompt) (it carries the summary so far) and HumanMessage(transcript).")
        r.passed("summarise_old", "Old messages became a short summary, and left the state.")
    r.task("summarise_old", check)
