import r
from fake_openai import Reply

BIG = {"job": "J-9", "work": "Replace the main", "street": "Station Road", "estimate": 65000}


def _app(fake):
    from langgraph.checkpoint.memory import InMemorySaver
    from repair import build_graph
    fake.script = lambda b: Reply("Replace 40 m of main on Station Road.")
    return build_graph(InMemorySaver())


def test_pause_for_engineer(fake):
    def check():
        app = _app(fake)
        config = {"configurable": {"thread_id": "J-9"}}
        state = app.invoke(BIG, config)
        asked = state.get("__interrupt__")
        if not asked:
            return r.failed("pause_for_engineer", "A Rs 65,000 repair went ahead without the engineer. In approval, call "
                            "interrupt({...}) and use its answer.", "a pause", state.get("status"))
        value = asked[0].value
        if not isinstance(value, dict) or value.get("estimate") != 65000 or value.get("brief") != "Replace 40 m of main on Station Road.":
            return r.failed("pause_for_engineer", "Send the engineer what she needs: the job, the estimate and the brief.",
                            {"job": "J-9", "estimate": 65000, "brief": "..."}, value)
        if app.get_state(config).next != ("approval",):
            return r.failed("pause_for_engineer", "The run should be paused at approval.", ("approval",), app.get_state(config).next)
        small = app.invoke({**BIG, "job": "J-10", "estimate": 1200}, {"configurable": {"thread_id": "J-10"}})
        if small.get("status") != "scheduled":
            return r.failed("pause_for_engineer", "Small repairs should still be scheduled without a pause.", "scheduled", small.get("status"))
        r.passed("pause_for_engineer", "The run stopped at approval and saved itself, with the question for the engineer.")
    r.task("pause_for_engineer", check)


def test_resume_with_decision(fake):
    def check():
        from repair import decide
        app = _app(fake)
        app.invoke(BIG, {"configurable": {"thread_id": "J-9"}})
        app.invoke({**BIG, "job": "J-11"}, {"configurable": {"thread_id": "J-11"}})
        yes = decide(app, "J-9", True, "before the festival")
        no = decide(app, "J-11", False, "no budget")
        if (yes or {}).get("status") != "scheduled (before the festival)" or (no or {}).get("status") != "refused: no budget":
            return r.failed("resume_with_decision", "Resume with app.invoke(Command(resume={\"approve\": approve, \"note\": note}), "
                            "{\"configurable\": {\"thread_id\": job}}) (finish pause_for_engineer first).",
                            "scheduled (before the festival) / refused: no budget",
                            f"{(yes or {}).get('status')} / {(no or {}).get('status')}")
        r.passed("resume_with_decision", "Her answer reached the paused node, and each job went its own way.")
    r.task("resume_with_decision", check)
