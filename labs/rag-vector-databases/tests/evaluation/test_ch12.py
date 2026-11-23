import r


def test_hit_rate():
    def check():
        import fieldbook as fb
        cases = [(([["a", "b"], ["c"]], [["b"], ["d"]], 2), 0.5), (([["a", "b"], ["c"]], [["b"], ["d"]], 1), 0.0),
                 (([["x", "y", "z"], ["p", "q"], ["m"]], [["z", "w"], ["q"], ["m"]], 3), 1.0),
                 (([["x", "y", "z"], ["p", "q"], ["m"]], [["z", "w"], ["q"], ["m"]], 2), 2 / 3)]
        for (results, expected, k), want in cases:
            got = fb.hit_rate(results, expected, k=k)
            if not r.close(got, want):
                return r.failed("hit_rate", f"hit_rate({results}, {expected}, k={k}): only the first k results count, and one right id is enough.",
                                round(want, 3), round(got, 3))
        r.passed("hit_rate", "Hit rate at k: did the right chunk make it into what the model will read?")
    r.task("hit_rate", check)


def test_mrr():
    def check():
        import fieldbook as fb
        cases = [(([["a", "b"], ["c", "d"]], [["b"], ["x"]]), 0.25), (([["a"], ["b"]], [["a"], ["b"]]), 1.0),
                 (([["q", "a", "b"]], [["a", "b"]]), 0.5), (([["q", "w", "e", "r"]], [["r"]]), 0.25)]
        for (results, expected), want in cases:
            got = fb.mrr(results, expected)
            if not r.close(got, want):
                tip = ("Only the first right id counts: [q, a, b] with a and b right scores 1/2, not 1/2 + 1/3."
                       if results == [["q", "a", "b"]] else "Add 1 / position of the first right id (positions start at 1), then average.")
                return r.failed("mrr", f"{tip} mrr({results}, {expected})", round(want, 3), round(got, 3))
        r.passed("mrr", "MRR rewards putting the right chunk first, not just somewhere: the measure for what the model reads first.")
    r.task("mrr", check)
