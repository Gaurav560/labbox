import json

import r
from fake_openai import Reply


def test_golden_eval():
    def check():
        from evals import pass_rate
        golden = [("q1", "10 days", None), ("q2", "Approval", None), ("q3", "1,000", None), ("q4", "3 working days", None)]
        answers = ["Wait 10 DAYS.", "It needs the manager's approval.", "It costs Rs 1000.", "Within 3 working days."]
        got = pass_rate(answers, golden)
        if abs(got - 0.75) > 1e-9:
            return r.failed("golden_eval", "Count answers containing their phrase (the second item), ignoring capitals, and divide by the number of questions.", 0.75, got)
        r.passed("golden_eval", "\"Rs 1000\" failed the phrase \"1,000\": a phrase check is cheap, and strict in ways you must read.")
    r.task("golden_eval", check)


def test_judge_answer(fake):
    def check():
        from evals import Grade, judge
        fake.script = lambda b: Reply(json.dumps({"correct": False, "reason": "The rule needs the manager's approval."}))
        got = judge("Can I store 80 crates?", "Yes, at the counter.", "Bookings of more than 50 crates need the manager's approval.")
        if not isinstance(got, Grade):
            return r.failed("judge_answer", "Return model.with_structured_output(Grade).invoke(JUDGE.format(...)): a Grade.", "Grade", type(got).__name__)
        sent = " ".join(fake.texts(fake.chat_requests[-1], "user"))
        if "manager's approval" not in sent or "at the counter" not in sent or "80 crates" not in sent:
            return r.failed("judge_answer", "Send JUDGE.format(rule=rule, question=question, answer=answer): the judge needs all three.")
        if got.correct:
            return r.failed("judge_answer", "Return the judge's Grade as it came back.")
        r.passed("judge_answer", "A second model grading the first against the rule: it reads meaning, where a phrase check reads letters.")
    r.task("judge_answer", check)
