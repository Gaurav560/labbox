import json

import r
from fake_openai import Reply


def test_check_claims(fake):
    def check():
        from reflection import CHECK, check as check_fn
        fake.script = lambda b: Reply(json.dumps({"sentences": [
            {"text": "The crew visits Wednesday 8:00 to 11:00.", "kind": "from_tools"},
            {"text": "Your water will be back tomorrow.", "kind": "new_claim"},
            {"text": "Happy to help!", "kind": "courtesy"}]}))
        got = check_fn("The crew visits Wednesday 8:00 to 11:00. Your water will be back tomorrow. Happy to help!",
                       "T-4471: crew assigned; East zone crew 2; Wednesday 8:00 to 11:00")
        if got != ["Your water will be back tomorrow."]:
            return r.failed("check_claims", "Return the text of every sentence the model labelled new_claim, and nothing else.",
                            ["Your water will be back tomorrow."], got)
        body = fake.chat_requests[-1]
        user = " ".join(fake.texts(body, "user"))
        if fake.texts(body, "system") != [CHECK] or "Tool results" not in user or "back tomorrow" not in user:
            return r.failed("check_claims", "Send SystemMessage(CHECK) and one HumanMessage with the tool results and the answer.")
        r.passed("check_claims", "The model labels each sentence; Python decides what counts as a problem.")
    r.task("check_claims", check)


def test_revise_or_finish(fake):
    def check():
        from langchain.messages import AIMessage
        from langgraph.graph import END
        import reflection
        state = {"messages": [AIMessage("Your water will be back tomorrow.")]}
        reflection.check = lambda answer, tools: []
        done = reflection.check_answer(state)
        reflection.check = lambda answer, tools: ["Your water will be back tomorrow."]
        again = reflection.check_answer(state)
        out = reflection.check_answer({**state, "rounds": reflection.MAX_ROUNDS})
        if done.goto != END:
            return r.failed("revise_or_finish", "With no problems, the answer is sent: Command(goto=END).", END, done.goto)
        msgs = (again.update or {}).get("messages", [])
        if again.goto != "agent" or not msgs or "back tomorrow" not in msgs[0].content or again.update.get("rounds") != 1:
            return r.failed("revise_or_finish", "With problems, go back to the agent with the feedback message and rounds + 1.",
                            "agent, with the feedback", again.goto)
        if out.goto != "hand_over":
            return r.failed("revise_or_finish", "After MAX_ROUNDS rewrites, stop and hand over to a person.", "hand_over", out.goto)
        r.passed("revise_or_finish", "Send it, rewrite it, or hand it to a person: three exits, and no endless loop.")
    r.task("revise_or_finish", check)
