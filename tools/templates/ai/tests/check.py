"""Hidden checks for an AI lab. The learner's code gets a fake OpenAI-style client that records the
request and returns a canned reply, so the check is the same every time. Never prints the solution."""
import json
import sys
import traceback
from types import SimpleNamespace

sys.path.insert(0, "/check/workspace")
sys.dont_write_bytecode = True


def report(task, passed, message, expected=None, actual=None):
    result = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        result["expected"], result["actual"] = expected, actual
    print("@@RESULT " + json.dumps(result), flush=True)


class FakeClient:
    """Looks like openai.OpenAI() for chat.completions.create; remembers what it was sent."""

    def __init__(self, reply: str):
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self._reply = reply

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(role="assistant", content=self._reply)
        return SimpleNamespace(choices=[SimpleNamespace(index=0, message=message, finish_reason="stop")])


try:
    import bot

    client = FakeClient("A first edition is the first printing of a book.")
    got = bot.ask(client, "What is a first edition?")
    if not client.calls:
        report("ask", False, "ask() never called client.chat.completions.create.")
    else:
        call = client.calls[-1]
        msgs = call.get("messages") or []
        if call.get("model") != "lab-chat":
            report("ask", False, "Use the model alias lab-chat.", "lab-chat", repr(call.get("model")))
        elif [m.get("role") for m in msgs] != ["system", "user"]:
            report("ask", False, "Send two messages: the system rules, then the user's question.", "['system', 'user']", str([m.get("role") for m in msgs]))
        elif msgs[0].get("content") != bot.SYSTEM or msgs[1].get("content") != "What is a first edition?":
            report("ask", False, "The system message must be SYSTEM and the user message the question, unchanged.")
        elif got != "A first edition is the first printing of a book.":
            report("ask", False, "Return the text of the model's reply.", "the reply text", repr(got))
        else:
            report("ask", True, "Right model, right messages, reply returned.")
except Exception as e:
    traceback.print_exc()
    report("ask", False, f"bot.py failed: {type(e).__name__}: {e}")
