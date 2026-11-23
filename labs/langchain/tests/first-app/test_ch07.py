import r


def test_chat_model(fake):
    def check():
        from app import chat_model
        m = chat_model()
        if m is None:
            return r.failed("chat_model", "chat_model() returned None. Return init_chat_model(\"openai:ai-chat\", temperature=0).")
        if getattr(m, "model_name", None) != "ai-chat":
            return r.failed("chat_model", "Use the model \"openai:ai-chat\": the provider, a colon, then the model.", "ai-chat", getattr(m, "model_name", None))
        if getattr(m, "temperature", None) != 0:
            return r.failed("chat_model", "Set temperature=0.", 0, getattr(m, "temperature", None))
        m.invoke("Hello")
        if not fake.chat_requests:
            return r.failed("chat_model", "The model did not reach the gateway.")
        r.passed("chat_model", f"init_chat_model built a {type(m).__name__}; swap \"openai:\" for another provider and nothing else changes.")
    r.task("chat_model", check)


def test_system_message(fake):
    def check():
        from app import SYSTEM, ask, chat_model
        m = chat_model()
        if m is None:
            return r.failed("system_message", "First build the model (the task above).")
        fake.script = lambda b: "I can help with rates, storage and loans."
        got = ask(m, "What can you do?")
        if not fake.chat_requests:
            return r.failed("system_message", "ask(...) never called the model: call model.invoke([...]).")
        body = fake.chat_requests[-1]
        if fake.texts(body, "system") != [SYSTEM]:
            return r.failed("system_message", "Send a SystemMessage(SYSTEM) first.", [SYSTEM], fake.texts(body, "system"))
        if fake.texts(body, "user") != ["What can you do?"]:
            return r.failed("system_message", "Then a HumanMessage with the question.")
        if got != "I can help with rates, storage and loans.":
            return r.failed("system_message", "Return the reply's .content (a string), not the whole message.", "I can help with rates, storage and loans.", got)
        r.passed("system_message", "Messages as objects: SystemMessage, HumanMessage, and an AIMessage back.")
    r.task("system_message", check)
