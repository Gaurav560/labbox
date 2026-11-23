import r


def test_sdk_client(fake):
    def check():
        from sdk import client
        c = client()
        if c is None:
            return r.failed("sdk_client", "client() returned None. Return OpenAI(base_url=..., api_key=..., timeout=60, max_retries=2).")
        if str(c.base_url).rstrip("/") != fake.base_url:
            return r.failed("sdk_client", "Use base_url=os.environ[\"OPENAI_BASE_URL\"], so the client talks to LabBox's gateway.", fake.base_url, c.base_url)
        if c.api_key != "check-key":
            return r.failed("sdk_client", "Use api_key=os.environ[\"OPENAI_API_KEY\"].")
        if c.max_retries != 2 or float(c.timeout) != 60:
            return r.failed("sdk_client", "Set timeout=60 and max_retries=2.", "timeout 60, retries 2", f"timeout {c.timeout}, retries {c.max_retries}")
        r.passed("sdk_client", "A client with a timeout and retries: a busy gateway costs a short wait, not a crash.")
    r.task("sdk_client", check)


def test_sdk_ask(fake):
    def check():
        from sdk import SYSTEM, ask, client
        fake.script = lambda b: "Yes, tomatoes can be stored."
        c = client()
        if c is None:
            return r.failed("sdk_ask", "First build the client (the task above).")
        text, usage = ask(c, "Do you store tomatoes?")
        if not fake.chat_requests:
            return r.failed("sdk_ask", "ask(...) never called the model: call openai.chat.completions.create(...).")
        body = fake.chat_requests[-1]
        if body.get("model") != "ai-chat" or [m["role"] for m in body["messages"]] != ["system", "user"] or body["messages"][0]["content"] != SYSTEM:
            return r.failed("sdk_ask", "Call create(model=\"ai-chat\", messages=[system message, user question]).")
        if text != "Yes, tomatoes can be stored.":
            return r.failed("sdk_ask", "Return completion.choices[0].message.content as the text.", "Yes, tomatoes can be stored.", text)
        if getattr(usage, "prompt_tokens", None) != 42:
            return r.failed("sdk_ask", "Return completion.usage as the second value.")
        r.passed("sdk_ask", "Typed objects instead of dictionaries: completion.choices[0].message.content, and usage.prompt_tokens.")
    r.task("sdk_ask", check)
