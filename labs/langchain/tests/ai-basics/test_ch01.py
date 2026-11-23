import r


def test_rule_reply():
    def check():
        from rules import ONION, OFFICE, UNKNOWN, rule_reply
        cases = [("When is the OFFICE open?", OFFICE), ("Is it open on Saturday?", OFFICE), ("What is the onion rate?", ONION),
                 ("price of onions please", ONION), ("Can I book cold storage?", UNKNOWN)]
        for message, want in cases:
            got = rule_reply(message)
            if got != want:
                return r.failed("rule_reply", f"For {message!r} the rules should answer {want!r}. Lower-case the message first, "
                                "then test the office words, then the price words, then fall back to UNKNOWN.", want, got)
        r.passed("rule_reply", "Rules work for the words someone thought of. \"When can I come in?\" still gets UNKNOWN: no rule mentions it.")
    r.task("rule_reply", check)


def test_learn_threshold():
    def check():
        from learn import EXAMPLES, accuracy, learn_threshold
        got = learn_threshold(EXAMPLES)
        if got != 8:
            return r.failed("learn_threshold", "Try every rain value of the examples, keep the one with the best accuracy, and on a tie the "
                            "smaller one. For these examples 8 mm and 11 mm both get 11 of 12 right, so the answer is 8.", 8, got)
        other = [(1, False), (4, True), (7, True)]
        if learn_threshold(other) != 4:
            return r.failed("learn_threshold", "On other examples the best threshold changes: loop over the examples you were given, not fixed numbers.", 4, learn_threshold(other))
        r.passed("learn_threshold", f"Nobody wrote 8 mm into the code: the program found it in the examples ({accuracy(8, EXAMPLES):.0%} right). That is machine learning.")
    r.task("learn_threshold", check)
