import r


def test_fan_out_questions():
    def check():
        from langgraph.types import Send
        from team import fan_out
        sends = fan_out({"questions": ["What changed in April?", "Where are the leaks?", "What did the council decide?"]})
        ok = isinstance(sends, list) and len(sends) == 3 and all(isinstance(s, Send) and s.node == "research" for s in sends)
        if not ok or [s.arg for s in sends] != [{"question": "What changed in April?"}, {"question": "Where are the leaks?"},
                                                 {"question": "What did the council decide?"}]:
            return r.failed("fan_out_questions", "Return one Send(\"research\", {\"question\": q}) for each question.",
                            "3 Sends to research", len(sends) if isinstance(sends, list) else sends)
        r.passed("fan_out_questions", "Three questions, three researchers, all at the same time.")
    r.task("fan_out_questions", check)


def test_check_citations():
    def check():
        from team import check_citations
        report = ("**Leaks on Station Road**\n\nPressure was raised in April [pressure-log].\n\nThe pipe is old.\n\n"
                  "The council said yes [council-notes].\n\nLeaks cluster near the towers [field-notes, pressure-log].")
        got = check_citations(report, {"pressure-log", "field-notes", "council-minutes"})
        want = ["no source: The pipe is old.", "unknown source [council-notes]"]
        if got != want:
            return r.failed("check_citations", "One problem per paragraph with no [source], and one per cited name that is not a "
                            "real source.", want, got)
        r.passed("check_citations", "An uncited paragraph and an invented source were both caught, in Python.")
    r.task("check_citations", check)
