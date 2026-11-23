import r


def test_cosine():
    def check():
        from embeddings import cosine
        pairs = [(([1, 0], [1, 0]), 1.0), (([1, 0], [0, 1]), 0.0), (([1, 1], [-1, -1]), -1.0), (([3, 4], [6, 8]), 1.0)]
        for (a, b), want in pairs:
            got = cosine(a, b)
            if abs(got - want) > 1e-9:
                return r.failed("cosine", f"cosine({a}, {b}) should be {want}: the dot product divided by the product of the lengths.", want, got)
        r.passed("cosine", "1 means the same direction, 0 unrelated, -1 opposite. Length does not matter: [3, 4] and [6, 8] score 1.")
    r.task("cosine", check)


def test_closest_question():
    def check():
        from embeddings import VECTORS, closest_question
        faq = {"a": [1.0, 0.0], "b": [0.6, 0.8], "c": [0.0, 1.0]}
        got = closest_question([0.5, 0.9], faq)
        if got != "b":
            return r.failed("closest_question", "Return the key whose vector has the highest cosine with the query.", "b", got)
        q = VECTORS["queries"]
        ok = closest_question(q["kanda bhav kay aahe aaj?"], VECTORS["faq"])
        r.passed("closest_question", f"\"kanda bhav kay aahe aaj?\" found {ok!r}: no word in common, the same meaning.")
    r.task("closest_question", check)
