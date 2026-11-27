import r
from fake_openai import Reply


def test_find_clauses():
    def check():
        from lookup import find_clauses, load_clauses
        c = load_clauses()
        cases = [("Is a cracked windscreen paid without the deductible?", ["C4", "C3", "C9"]),
                 ("My scooter was stolen. What must I send?", ["C2", "C5"]),
                 ("Do we pay for a puncture?", [])]
        for q, want in cases:
            got = find_clauses(q, c)
            if got != want:
                if want == [] and got:
                    return r.failed("find_clauses", f"No clause shares a meaningful word with {q!r}: leave out clauses with a score of 0, so nothing is returned.",
                                    want, got)
                return r.failed("find_clauses", f"For {q!r}: score each clause by the words it shares with the question (title and text), "
                                "highest first, ties in clause order, at most k.", want, got)
        if find_clauses("theft police complaint stolen", c, k=1) != ["C2"]:
            return r.failed("find_clauses", "Use the k argument: with k=1, only the best clause.", ["C2"], find_clauses("theft police complaint stolen", c, k=1))
        r.passed("find_clauses", "The model will see three relevant clauses instead of the whole wording: cheaper, and easier to check.")
    r.task("find_clauses", check)


def test_cited_answer(fake):
    def check():
        from lookup import cited_answer, load_clauses
        c = load_clauses()
        q = "Is a cracked windscreen paid without the deductible?"
        fake.script = lambda b: Reply("Yes. Glass-only claims are paid without the deductible [C4], unlike others [C3] [C4].")
        got = cited_answer(q, c)
        if not fake.chat_requests:
            return r.failed("cited_answer", "cited_answer did not call the model.")
        user = " ".join(fake.texts(fake.chat_requests[-1], "user"))
        if "[C4] Glass:" not in user or "[C3] Deductible:" not in user or "[C12]" in user:
            return r.failed("cited_answer", "Send the found clauses, one per line as \"[C4] Glass: text\", and only those.", "[C4] Glass: ...", user[:200])
        if got.get("cited") != ["C4", "C3"] or got.get("ok") is not True:
            return r.failed("cited_answer", "cited is the clause ids in the answer, in order, without repeats; ok is True when there is at least one and all were given.",
                            {"cited": ["C4", "C3"], "ok": True}, {k: got.get(k) for k in ("cited", "ok")})
        fake.script = lambda b: Reply("Yes, glass is always covered [C12].")
        got = cited_answer(q, c)
        if got.get("ok") is not False:
            return r.failed("cited_answer", "The answer cites C12, which the model was not given: ok must be False (the citation cannot be checked).", False, got.get("ok"))
        fake.script = lambda b: Reply("Yes, it is covered.")
        got = cited_answer(q, c)
        if got.get("ok") is not False or got.get("cited") != []:
            return r.failed("cited_answer", "An answer with no citation is not ok: nobody can check where it came from.", {"cited": [], "ok": False}, got)
        r.passed("cited_answer", "Every answer now points to its clause, and an answer that points nowhere, or somewhere it was not shown, is flagged.")
    r.task("cited_answer", check)
