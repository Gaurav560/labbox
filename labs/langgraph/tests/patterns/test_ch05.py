import json

import r
from fake_openai import Reply


def test_parallel_branches():
    def check():
        from graph import build_parallel
        try:
            g = build_parallel()
        except ValueError:
            return r.failed("parallel_branches", "The graph has no edge from START yet: add START -> zone_lookup and START -> history_lookup, then join both into assign.")
        final = g.invoke({"street": "Station Road"})
        if final.get("plan") != "South zone crew and a survey of the old main (repeated complaints)":
            return r.failed("parallel_branches", "assign needs both the zone and the history: connect START to both lookups, and both to assign.",
                            "South zone crew and a survey...", final.get("plan"))
        first = list(g.stream({"street": "Tilak Nagar"}, stream_mode="updates"))
        if sorted(first[0]) != ["history_lookup", "zone_lookup"] and sorted(list(first[0]) + list(first[1])) != ["history_lookup", "zone_lookup"]:
            return r.failed("parallel_branches", "Both lookups should start from START, in the same step.")
        if list(first[-1]) != ["assign"] or sum(1 for u in first if "assign" in u) != 1:
            return r.failed("parallel_branches", "assign should run once, after both lookups: graph.add_edge([\"zone_lookup\", \"history_lookup\"], \"assign\").")
        r.passed("parallel_branches", "Two lookups in the same step, and assign waits for both: fan out, then join.")
    r.task("parallel_branches", check)


def test_evaluator_loop(fake):
    def check():
        from langgraph.graph import END
        from graph import MAX_DRAFTS, build_notice_loop, next_step
        if next_step({"good": True, "drafts": 1}) != END or next_step({"good": False, "drafts": MAX_DRAFTS}) != END:
            return r.failed("evaluator_loop", "Return END when the notice is good, or when MAX_DRAFTS drafts have been written.")
        if next_step({"good": False, "drafts": 1}) != "write_notice":
            return r.failed("evaluator_loop", "A notice that is not good yet should go back to write_notice.", "write_notice", next_step({"good": False, "drafts": 1}))
        grades = iter([{"good": False, "feedback": "Add the end time."}, {"good": True, "feedback": ""}])
        fake.script = lambda b: Reply(json.dumps(next(grades))) if b.get("response_format") else Reply(f"draft {len(fake.chat_requests)}")
        final = build_notice_loop().invoke({"facts": "Old Market, Thursday, 10 to 16"})
        if final.get("drafts") != 2 or not final.get("good"):
            return r.failed("evaluator_loop", "Rejected once, then accepted: there should be exactly 2 drafts.", 2, final.get("drafts"))
        writes = [b for b in fake.chat_requests if not b.get("response_format")]
        if "Add the end time." not in " ".join(fake.texts(writes[-1], "user")):
            return r.failed("evaluator_loop", "The second draft should be written with the grader's feedback.")
        r.passed("evaluator_loop", "A writer, a grader and a loop with a ceiling: rewritten once with the feedback, then accepted.")
    r.task("evaluator_loop", check)
