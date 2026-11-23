import r


def test_honest_prompt(fake):
    def check():
        from honest import FACTS, SYSTEM, ask, honest_prompt
        p = honest_prompt()
        if "I don't know" not in p:
            return r.failed("honest_prompt", "Give the model permission to not know: the prompt must contain \"I don't know\".")
        missing = [line for line in FACTS.strip().splitlines() if line not in p]
        if missing:
            return r.failed("honest_prompt", "Give the model the facts: add \"Facts:\" and every line of FACTS.", "all fact lines", f"missing {missing[0]!r}")
        if not p.startswith(SYSTEM):
            return r.failed("honest_prompt", "Start with SYSTEM, then add the instruction and the facts.")
        ask("What is the garlic rate?")
        if fake.texts(fake.chat_requests[-1], "system") != [p]:
            return r.failed("honest_prompt", "ask(...) should send honest_prompt() as the system message.")
        r.passed("honest_prompt", "Facts to answer from, and permission to say \"I don't know\": the two defences against invented answers.")
    r.task("honest_prompt", check)


def test_answer_cost(fake):
    def check():
        from honest import answer_cost
        from langchain.messages import AIMessage
        reply = AIMessage("x", usage_metadata={"input_tokens": 1000, "output_tokens": 200, "total_tokens": 1200})
        got = answer_cost(reply)
        want = (1000 * 0.15 + 200 * 0.60) / 1_000_000
        if abs(got - want) > 1e-12:
            return r.failed("answer_cost", "Input tokens times 0.15 plus output tokens times 0.60, divided by 1,000,000.", f"{want:.6f}", f"{got:.6f}")
        r.passed("answer_cost", f"1,000 tokens in and 200 out cost ${want:.6f}: output tokens are four times dearer.")
    r.task("answer_cost", check)
