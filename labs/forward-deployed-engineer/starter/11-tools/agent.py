"""Letting the model use Deccan Shield's systems: one tool, get_policy, and the loop that runs it.
Run it with: python agent.py"""
import json
import os
import sqlite3

from openai import OpenAI

MODEL = "ai-chat"  # the gateway's name for the model (gpt-4o-mini here); the gateway holds the real key
SYSTEM = (
    "You help Deccan Shield's adjusters. Use the get_policy tool to look up a policy before saying anything about it. "
    "Answer in at most three sentences."
)


def client():
    return OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"], timeout=60, max_retries=2)


def get_policy(policy_no, path="data/claimdesk.db"):
    """The policy as a dict, or None if there is no such policy."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()
    con.close()
    return dict(row) if row else None


# TODO (task policy_tool): describe get_policy to the model: a list with one tool, {"type": "function", "function":
# {"name": "get_policy", "description": ..., "parameters": a JSON schema object with one required string property,
# "policy_no"}}. Say in the description what it returns and the format of a policy number (DS-POL-12345).
TOOLS = []


def run_tool(name, arguments):
    """Runs the tool the model asked for and returns its result as a JSON string (what goes back to the model)."""
    # TODO (task policy_tool): for "get_policy", json.loads the arguments, call get_policy(args["policy_no"]) and return
    # json.dumps of the policy, or of {"error": "no policy DS-POL-..."} when it is None. Any other name:
    # json.dumps({"error": f"unknown tool {name}"}).
    return json.dumps({"error": "not written yet"})


def run_agent(question, openai=None, max_turns=4):
    """(answer, calls): asks the model; while it asks for tools, runs them and gives back the results; calls is the
    list of (tool name, arguments) in order. After max_turns model calls without an answer, it stops and says so."""
    # TODO (task tool_loop): messages starts with SYSTEM and the question. Each turn: create(model=MODEL, temperature=0,
    # messages=messages, tools=TOOLS). If the message has no tool_calls, return (message.content, calls). Otherwise append
    # the message itself, then for each tool call append {"role": "tool", "tool_call_id": call.id, "content":
    # run_tool(call.function.name, call.function.arguments)} and record the call. After max_turns, return
    # ("Stopped after 4 model calls without an answer.", calls) with the real number.
    return "", []


if __name__ == "__main__":
    for q in ["Is policy DS-POL-40185 in force on 4 October 2026, and what is its deductible?",
              "Who holds policy DS-POL-99999?"]:
        answer, calls = run_agent(q)
        print("Q:", q)
        print("   tool calls:", calls)
        print("   answer:", answer)
