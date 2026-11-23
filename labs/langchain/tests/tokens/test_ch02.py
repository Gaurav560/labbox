import r


def test_count_tokens():
    def check():
        from tokens import count_tokens
        got = count_tokens("What is the onion rate today?")
        if got != 7:
            return r.failed("count_tokens", "Return len(ENCODING.encode(text)).", 7, got)
        if count_tokens("") != 0:
            return r.failed("count_tokens", "An empty text is 0 tokens.", 0, count_tokens(""))
        r.passed("count_tokens", "7 tokens for an English question. Run main.py and compare the same question in Marathi.")
    r.task("count_tokens", check)


def test_fit_window():
    def check():
        from tokens import count_tokens, fit_window
        chat = ["Hello, I am Ravi from Lasalgaon.", "I grow onions on 3 acres.", "My cold storage booking is 40 crates.",
                "Can I add 20 more crates next week?"]
        got = fit_window(chat, 25)
        want = chat[2:]
        if got != want:
            return r.failed("fit_window", "Keep the newest messages that fit in 25 tokens, in their original order: walk backwards from "
                            "the last one and stop at the first that does not fit.", want, got)
        if fit_window(chat, 5) != []:
            return r.failed("fit_window", "If even the newest message does not fit, keep nothing.", [], fit_window(chat, 5))
        r.passed("fit_window", f"The window keeps the newest {sum(count_tokens(m) for m in got)} tokens; the oldest messages fall out first.")
    r.task("fit_window", check)
