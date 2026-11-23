import json

import r
from fake_openai import Reply


def _state(rewrites=0):
    from langchain.messages import AIMessage, HumanMessage, ToolMessage
    return {"messages": [HumanMessage("The thing on my roof overflows."),
                         AIMessage("", tool_calls=[{"name": "search_rules", "args": {"query": "overflow"}, "id": "c1"}]),
                         ToolMessage("New connections: Rs 1,500.", tool_call_id="c1")], "rewrites": rewrites}


def test_grade_documents(fake):
    def check():
        from rag import GRADE, grade_documents
        fake.script = lambda b: Reply(json.dumps({"relevant": False}))
        first = grade_documents(_state(0))
        body = fake.chat_requests[-1] if fake.chat_requests else {}
        later = grade_documents(_state(1))
        fake.script = lambda b: Reply(json.dumps({"relevant": True}))
        good = grade_documents(_state(0))
        if (first, later, good) != ("rewrite_question", "answer", "answer"):
            return r.failed("grade_documents", "Irrelevant and no rewrite yet: \"rewrite_question\"; relevant, or a rewrite was "
                            "already tried: \"answer\".", ("rewrite_question", "answer", "answer"), (first, later, good))
        user = " ".join(fake.texts(body, "user"))
        if fake.texts(body, "system") != [GRADE] or "roof" not in user or "New connections" not in user:
            return r.failed("grade_documents", "Ask with SystemMessage(GRADE) and a HumanMessage holding the question and the text found.")
        r.passed("grade_documents", "The search result is checked before anyone answers from it.")
    r.task("grade_documents", check)


def test_rewrite_question(fake):
    def check():
        from rag import REWRITE, rewrite_question
        fake.script = lambda b: Reply("roof tank overflow float valve responsibility")
        update = rewrite_question(_state(0))
        msgs = update.get("messages", [])
        if not msgs or msgs[0].type != "human" or msgs[0].content != "roof tank overflow float valve responsibility":
            return r.failed("rewrite_question", "Return the model's rewrite as a HumanMessage in messages.",
                            "roof tank overflow float valve responsibility", msgs[0].content if msgs else None)
        if update.get("rewrites") != 1 or fake.texts(fake.chat_requests[-1], "system") != [REWRITE]:
            return r.failed("rewrite_question", "Use SystemMessage(REWRITE), and count the rewrite (rewrites + 1).")
        r.passed("rewrite_question", "A vague question became a search the rulebook can match.")
    r.task("rewrite_question", check)
