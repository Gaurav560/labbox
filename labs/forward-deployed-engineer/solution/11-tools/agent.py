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


TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_policy",
        "description": ("Looks up one Deccan Shield motor policy by its number (like DS-POL-40185). Returns the holder, "
                        "vehicle registration, vehicle type, start_date and end_date (YYYY-MM-DD), sum_insured and "
                        "deductible in rupees, or an error if there is no such policy."),
        "parameters": {
            "type": "object",
            "properties": {"policy_no": {"type": "string", "description": "The policy number, like DS-POL-40185"}},
            "required": ["policy_no"],
        },
    },
}]


def run_tool(name, arguments):
    """Runs the tool the model asked for and returns its result as a JSON string (what goes back to the model)."""
    if name != "get_policy":
        return json.dumps({"error": f"unknown tool {name}"})
    args = json.loads(arguments)
    policy = get_policy(args["policy_no"])
    return json.dumps(policy if policy else {"error": f"no policy {args['policy_no']}"})


def run_agent(question, openai=None, max_turns=4):
    """(answer, calls): asks the model; while it asks for tools, runs them and gives back the results; calls is the
    list of (tool name, arguments) in order. After max_turns model calls without an answer, it stops and says so."""
    openai = openai or client()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    calls = []
    for _ in range(max_turns):
        message = openai.chat.completions.create(model=MODEL, temperature=0, messages=messages, tools=TOOLS).choices[0].message
        if not message.tool_calls:
            return message.content, calls
        messages.append(message)
        for call in message.tool_calls:
            calls.append((call.function.name, call.function.arguments))
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": run_tool(call.function.name, call.function.arguments)})
    return f"Stopped after {max_turns} model calls without an answer.", calls


if __name__ == "__main__":
    for q in ["Is policy DS-POL-40185 in force on 4 October 2026, and what is its deductible?",
              "Who holds policy DS-POL-99999?"]:
        answer, calls = run_agent(q)
        print("Q:", q)
        print("   tool calls:", calls)
        print("   answer:", answer)
