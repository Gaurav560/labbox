from types import SimpleNamespace

import r
from fake_openai import Reply


def test_ask_model(fake):
    def check():
        import gateway
        fake.script = lambda b: Reply("A deductible is the part of a claim the customer pays.", usage=(42, 8))
        answer, usage = gateway.ask("What is a deductible?")
        if not fake.chat_requests:
            return r.failed("ask_model", "ask() did not call the model. Use openai.chat.completions.create(...) with the client.")
        req = fake.chat_requests[-1]
        if req.get("model") != "ai-chat":
            return r.failed("ask_model", "Send model=MODEL (\"ai-chat\"): the gateway knows the model by that name.", "ai-chat", req.get("model"))
        if req.get("temperature") != 0:
            return r.failed("ask_model", "Pass temperature=0, so the same question gives the same answer while you build.", 0, req.get("temperature"))
        roles = [m.get("role") for m in req.get("messages", [])]
        if roles != ["system", "user"] or fake.texts(req, "system") != [gateway.SYSTEM] or fake.texts(req, "user") != ["What is a deductible?"]:
            return r.failed("ask_model", "Two messages: SYSTEM as the system message, then the question as the user message.",
                            ["system", "user"], roles)
        if answer != "A deductible is the part of a claim the customer pays." or getattr(usage, "prompt_tokens", None) != 42:
            return r.failed("ask_model", "Return completion.choices[0].message.content and completion.usage.",
                            "the answer and the usage", (answer, usage))
        r.passed("ask_model", "One request through the gateway: your code never saw an API key, and every token was counted.")
    r.task("ask_model", check)


def test_call_cost():
    def check():
        import gateway
        u = SimpleNamespace(prompt_tokens=1000, completion_tokens=500)
        got = gateway.cost_rs(u)
        if abs(got - 0.0396) > 1e-9:
            swapped = (1000 * 0.60 + 500 * 0.15) / 1e6 * 88
            if abs(got - swapped) < 1e-9:
                return r.failed("call_cost", "The prices are swapped: input tokens cost USD_PER_MILLION_IN, output tokens USD_PER_MILLION_OUT.", 0.0396, got)
            return r.failed("call_cost", "1000 tokens in at $0.15 per million and 500 out at $0.60 per million is $0.00045, times 88 is Rs 0.0396.",
                            0.0396, got)
        m = gateway.monthly_rs(u, 80)
        if m != 95.04:
            return r.failed("call_cost", "80 calls a day for 30 days at Rs 0.0396 each is Rs 95.04: cost_rs(usage) * calls_per_day * days, rounded to 2 places.",
                            95.04, m)
        if gateway.monthly_rs(u, 10, days=7) != 2.77:
            return r.failed("call_cost", "Use the days argument too: 10 calls a day for 7 days is Rs 2.77.", 2.77, gateway.monthly_rs(u, 10, days=7))
        r.passed("call_cost", "Now every model call has a price in rupees, the language Deccan Shield's budget is written in.")
    r.task("call_cost", check)
