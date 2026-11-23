import r


def test_log_reducer():
    def check():
        from graph import build_graph
        final = build_graph().invoke({"text": "Small leak behind the school"})
        log = final.get("log")
        want = ["classify: leak", "check_location: near a hospital or school"]
        if log != want:
            return r.failed("log_reducer", "Each node's {\"log\": [...]} should be added to the list, not replace it: log: Annotated[list[str], operator.add].",
                            want, log)
        r.passed("log_reducer", "A reducer says how an update joins the state: here, lists are added together.")
    r.task("log_reducer", check)


def test_severity_reducer():
    def check():
        from graph import build_graph, higher
        cases = [("", "high", "high"), ("urgent", "high", "urgent"), ("normal", "high", "high"), ("high", "high", "high")]
        for current, new, want in cases:
            got = higher(current, new)
            if got != want:
                return r.failed("severity_reducer", f"higher({current!r}, {new!r}) should keep the more serious one.", want, got)
        final = build_graph().invoke({"text": "Brown water near the district hospital"})
        if final.get("severity") != "urgent":
            return r.failed("severity_reducer", "Dirty water is urgent; check_location's \"high\" must not lower it.", "urgent", final.get("severity"))
        r.passed("severity_reducer", "Severity can only go up: a later node's \"high\" cannot hide an urgent complaint.")
    r.task("severity_reducer", check)
