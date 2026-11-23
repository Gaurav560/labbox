import r
from fake_openai import Reply


def test_remember_fact(fake):
    def check():
        from langgraph.store.memory import InMemoryStore
        from navin import Member, navin_agent
        store = InMemoryStore()
        agent = navin_agent(store=store)
        fake.script = lambda b: Reply.tool("remember", {"fact": "grows onions on 3 acres"}) if len(fake.chat_requests) == 1 else Reply("Noted.")
        agent.invoke({"messages": [{"role": "user", "content": "I grow onions on 3 acres."}]}, {"configurable": {"thread_id": "a"}},
                     context=Member("M-104", "Ravi Patil"))
        facts = [i.value for i in store.search(("M-104", "facts"))]
        if facts != [{"fact": "grows onions on 3 acres"}]:
            return r.failed("remember_fact", "Save {\"fact\": fact} with runtime.store.put((member id, \"facts\"), key, value).",
                            [{"fact": "grows onions on 3 acres"}], facts)
        fake.reset(); fake.script = lambda b: Reply("Hello Ravi.")
        agent.invoke({"messages": [{"role": "user", "content": "Hello"}]}, {"configurable": {"thread_id": "new-thread"}}, context=Member("M-104", "Ravi Patil"))
        system = " ".join(fake.texts(fake.chat_requests[-1], "system"))
        if "grows onions on 3 acres" not in system:
            return r.failed("remember_fact", "The fact should reach the next conversation through the member's prompt.")
        r.passed("remember_fact", "A fact saved in one conversation, known in the next: long-term memory, kept per member.")
    r.task("remember_fact", check)


def test_chat_endpoint(fake):
    def check():
        from fastapi.testclient import TestClient
        import app as web
        client = TestClient(web.app)
        fake.script = lambda b: Reply("Hello Ravi, how can I help?")
        res = client.post("/chat", json={"member_id": "M-104", "message": "Hello"})
        if res.status_code != 200:
            return r.failed("chat_endpoint", f"POST /chat answered {res.status_code}.", 200, res.status_code)
        if res.json() != {"status": "answered", "answer": "Hello Ravi, how can I help?"}:
            return r.failed("chat_endpoint", "Run the agent with the member's message, thread and context, and return reply(result).",
                            {"status": "answered", "answer": "Hello Ravi, how can I help?"}, res.json())
        if "Ravi Patil (M-104)" not in " ".join(fake.texts(fake.chat_requests[-1], "system")):
            return r.failed("chat_endpoint", "Pass context=Member(member_id, name) so the prompt knows who is asking.")
        fake.reset()
        fake.script = lambda b: Reply.tool("book_storage", {"crates": 80, "days": 10, "crop": "onion"}) if len(fake.chat_requests) == 1 else Reply("Booked.")
        res = client.post("/chat", json={"member_id": "M-221", "message": "Book 80 crates"})
        if res.json().get("status") != "waiting_for_manager":
            return r.failed("chat_endpoint", "A booking should come back as waiting_for_manager.", "waiting_for_manager", res.json())
        res = client.post("/manager/decide", json={"member_id": "M-221", "decision": {"type": "approve"}})
        if res.json() != {"status": "answered", "answer": "Booked."}:
            return r.failed("chat_endpoint", "After the manager approves, the same thread should finish.", {"status": "answered", "answer": "Booked."}, res.json())
        r.passed("chat_endpoint", "Navin is a web service: members chat, bookings wait for the manager, and each member has their own thread.")
    r.task("chat_endpoint", check)
