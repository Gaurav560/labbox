import r
from fake_openai import Reply


def script(fake):
    return lambda b: Reply.tool("book_storage", {"crates": 80, "days": 10, "crop": "onion"}) if len(fake.chat_requests) == 1 else Reply("Done.")


def test_approval_middleware(fake):
    def check():
        import booking
        from agent import booking_agent
        booking.BOOKINGS.clear()
        fake.script = script(fake)
        result = booking_agent().invoke({"messages": [{"role": "user", "content": "book 80"}]}, {"configurable": {"thread_id": "t"}})
        if booking.BOOKINGS:
            return r.failed("approval_middleware", "The booking ran without the manager. Add HumanInTheLoopMiddleware(interrupt_on={\"book_storage\": {...}}).")
        if not result.get("__interrupt__"):
            return r.failed("approval_middleware", "The run should pause with an __interrupt__ waiting for a decision.")
        review = result["__interrupt__"][0].value["review_configs"][0]
        if sorted(review["allowed_decisions"]) != ["approve", "edit", "reject"]:
            return r.failed("approval_middleware", "Allow all three decisions: approve, edit and reject.", ["approve", "edit", "reject"], review["allowed_decisions"])
        r.passed("approval_middleware", "The agent stopped at the booking, saved its state, and is waiting for the manager.")
    r.task("approval_middleware", check)


def test_resume_decision(fake):
    def check():
        import booking
        from agent import booking_agent, manager_decides
        agent = booking_agent()
        for decision, want in [({"type": "approve"}, [{"crates": 80, "days": 10, "crop": "onion"}]),
                               ({"type": "edit", "edited_action": {"name": "book_storage", "args": {"crates": 50, "days": 10, "crop": "onion"}}},
                                [{"crates": 50, "days": 10, "crop": "onion"}]),
                               ({"type": "reject", "message": "full"}, [])]:
            booking.BOOKINGS.clear(); fake.reset(); fake.script = script(fake)
            thread = decision["type"]
            agent.invoke({"messages": [{"role": "user", "content": "book 80"}]}, {"configurable": {"thread_id": thread}})
            result = manager_decides(agent, thread, decision)
            if result is None:
                return r.failed("resume_decision", "manager_decides returned None. Return agent.invoke(Command(resume={\"decisions\": [decision]}), config).")
            if booking.BOOKINGS != want:
                return r.failed("resume_decision", f"After {decision['type']}, the bookings should be {want}: resume the same thread with the decision.", want, booking.BOOKINGS)
        r.passed("resume_decision", "Approve books it, edit books what the manager changed, reject books nothing and tells the model why.")
    r.task("resume_decision", check)
