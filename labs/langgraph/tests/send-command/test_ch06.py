import r


def test_fan_out():
    def check():
        from langgraph.types import Send
        from graph import build_storm_graph, fan_out
        sends = fan_out({"complaints": ["a leak", "brown water"]})
        if not sends or not all(isinstance(s, Send) for s in sends) or [s.arg for s in sends] != [{"text": "a leak"}, {"text": "brown water"}]:
            return r.failed("fan_out", "Return one Send(\"triage_one\", {\"text\": text}) per complaint.", 2, len(sends or []))
        final = build_storm_graph().invoke({"complaints": ["Pipe burst", "No water", "Brown water", "Bill wrong"]})
        if len(final.get("tickets", [])) != 4 or final.get("summary") != "4 complaints, 1 urgent":
            return r.failed("fan_out", "Every complaint should get its own triage, and all tickets should reach summarise.",
                            "4 complaints, 1 urgent", final.get("summary"))
        r.passed("fan_out", "One Send per complaint: the same node ran four times, each with its own small state.")
    r.task("fan_out", check)


def test_command_goto():
    def check():
        from graph import build_repair_graph
        g = build_repair_graph()
        big = g.invoke({"kind": "no_water", "estimate": 65000})
        small = g.invoke({"kind": "leak", "estimate": 18000})
        if big.get("status") != "waiting for the engineer (sent to the executive engineer)":
            return r.failed("command_goto", "A repair over Rs 50,000 should go to engineer_approval: Command(goto=..., update=...).",
                            "waiting for the engineer (sent to the executive engineer)", big.get("status"))
        if small.get("status") != "scheduled for tomorrow":
            return r.failed("command_goto", "A smaller repair goes to schedule.", "scheduled for tomorrow", small.get("status"))
        r.passed("command_goto", "The node chose where to go and what to write, in one return value.")
    r.task("command_goto", check)
