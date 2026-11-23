import json

import r
from fake_openai import Reply


def _script(fake, language):
    def answer(b):
        if b.get("response_format"):
            return Reply(json.dumps({"language": language}))
        return Reply("reply")
    fake.script = answer


def test_save_preference(fake):
    def check():
        from langgraph.store.memory import InMemoryStore
        from chat import Citizen, build_graph
        store = InMemoryStore()
        _script(fake, "Marathi")
        build_graph(store).invoke({"messages": [("user", "Reply in Marathi please")]}, {"configurable": {"thread_id": "a"}},
                                  context=Citizen("98220"))
        item = store.get(("citizens", "98220"), "profile")
        if item is None or item.value != {"language": "Marathi"}:
            return r.failed("save_preference", "Save the language: runtime.store.put((\"citizens\", runtime.context.phone), "
                            "\"profile\", {\"language\": prefs.language}).", {"language": "Marathi"}, item and item.value)
        _script(fake, None)
        build_graph(store).invoke({"messages": [("user", "Pipe leaking")]}, {"configurable": {"thread_id": "b"}},
                                  context=Citizen("70300"))
        if store.get(("citizens", "70300"), "profile") is not None:
            return r.failed("save_preference", "Save only when the citizen asked for a language (prefs.language is set).")
        r.passed("save_preference", "The preference went into the store, under this citizen's phone number.")
    r.task("save_preference", check)


def test_use_preference(fake):
    def check():
        from langgraph.store.memory import InMemoryStore
        from chat import Citizen, build_graph
        store = InMemoryStore()
        store.put(("citizens", "98220"), "profile", {"language": "Marathi"})
        _script(fake, None)
        build_graph(store).invoke({"messages": [("user", "Pipe leaking")]}, {"configurable": {"thread_id": "new"}},
                                  context=Citizen("98220"))
        system = " ".join(fake.texts(fake.chat_requests[-1], "system"))
        if "Reply in Marathi" not in system:
            return r.failed("use_preference", "In respond, read runtime.store.get((\"citizens\", runtime.context.phone), \"profile\") "
                            "and put its language into SYSTEM.", "Reply in Marathi", system[:60])
        build_graph(store).invoke({"messages": [("user", "Pipe leaking")]}, {"configurable": {"thread_id": "x"}},
                                  context=Citizen("70300"))
        if "Reply in English" not in " ".join(fake.texts(fake.chat_requests[-1], "system")):
            return r.failed("use_preference", "A citizen with no profile gets English.")
        r.passed("use_preference", "A brand-new thread already knew the citizen's language, from the store.")
    r.task("use_preference", check)
