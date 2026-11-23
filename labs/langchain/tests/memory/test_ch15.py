import r
from fake_openai import Reply


def test_memory_agent(fake):
    def check():
        from memory import memory_agent
        agent = memory_agent()
        if agent is None:
            return r.failed("memory_agent", "memory_agent() returned None. Build chapter 11's agent with checkpointer=InMemorySaver().")
        if agent.checkpointer is None:
            return r.failed("memory_agent", "Add checkpointer=InMemorySaver(): without it the agent forgets everything after each call.")
        fake.script = lambda b: Reply("ok")
        cfg = {"configurable": {"thread_id": "t"}}
        agent.invoke({"messages": [{"role": "user", "content": "I am Ravi"}]}, cfg)
        agent.invoke({"messages": [{"role": "user", "content": "Who am I?"}]}, cfg)
        users = fake.texts(fake.chat_requests[-1], "user")
        if users != ["I am Ravi", "Who am I?"]:
            return r.failed("memory_agent", "The second call should send the whole conversation of that thread.", ["I am Ravi", "Who am I?"], users)
        r.passed("memory_agent", "A checkpointer saves every step; the next call starts from the saved conversation.")
    r.task("memory_agent", check)


def test_thread_per_member(fake):
    def check():
        from memory import ask, memory_agent
        agent = memory_agent()
        if agent is None:
            return r.failed("thread_per_member", "First build the agent with a checkpointer (the task above).")
        fake.script = lambda b: Reply(f"reply {len(fake.chat_requests)}")
        ask(agent, "M-104", "I am Ravi")
        got = ask(agent, "M-221", "Who am I?")
        if not fake.chat_requests:
            return r.failed("thread_per_member", "ask(...) never called the agent.")
        users = fake.texts(fake.chat_requests[-1], "user")
        if users != ["Who am I?"]:
            return r.failed("thread_per_member", "Each member needs their own thread: pass {\"configurable\": {\"thread_id\": member_id}}. Asha must not see Ravi's messages.",
                            ["Who am I?"], users)
        if got != "reply 2":
            return r.failed("thread_per_member", "Return the last message's content.", "reply 2", got)
        ask(agent, "M-104", "And my name?")
        if fake.texts(fake.chat_requests[-1], "user") != ["I am Ravi", "And my name?"]:
            return r.failed("thread_per_member", "Ravi's thread should continue his own conversation.")
        r.passed("thread_per_member", "One thread per member: Ravi's conversation continues, Asha's starts clean, and neither sees the other's.")
    r.task("thread_per_member", check)
