import json

import r
from fake_openai import Reply


def test_supervisor_route(fake):
    def check():
        from langgraph.graph import END
        from team import MAX_TURNS, supervisor
        state = {"messages": [("user", "My bill doubled.")]}
        fake.script = lambda b: Reply(json.dumps({"next": "billing", "reason": "a bill"}))
        go = supervisor(state)
        capped = supervisor({**state, "turns": MAX_TURNS})
        fake.script = lambda b: Reply(json.dumps({"next": "FINISH", "reason": "done"}))
        stop = supervisor(state)
        if go.goto != "billing" or (go.update or {}).get("turns") != 1:
            return r.failed("supervisor_route", "Go to the chosen specialist and count the turn: Command(goto=route.next, "
                            "update={\"turns\": ... + 1}).", "billing, turns 1", (go.goto, go.update))
        if stop.goto != END or capped.goto != END:
            return r.failed("supervisor_route", "FINISH, or MAX_TURNS reached, ends the run: Command(goto=END).")
        r.passed("supervisor_route", "The supervisor picks who acts next, and knows when to stop.")
    r.task("supervisor_route", check)


def test_specialist_report(fake):
    def check():
        from offices import BILLING_TOOLS
        from team import BILLING, specialist
        fake.script = lambda b: Reply("August bill held for a meter check.")
        out = specialist("billing", BILLING, BILLING_TOOLS)({"messages": [("user", "My bill doubled.")]})
        msgs = (out.update or {}).get("messages", [])
        if out.goto != "supervisor" or not msgs or msgs[0].content != "August bill held for a meter check." or msgs[0].name != "billing":
            return r.failed("specialist_report", "Hand back to the supervisor with the report: Command(goto=\"supervisor\", "
                            "update={\"messages\": [report]}).", "the report, named billing", msgs)
        r.passed("specialist_report", "The specialist reports back under its own name, and the supervisor decides again.")
    r.task("specialist_report", check)
