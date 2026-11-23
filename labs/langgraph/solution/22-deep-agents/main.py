"""Chapter 22: the deep agent at work. Every tool call is printed; the plan ends up in data/plan.md."""
from planner import build_agent

agent = build_agent()
task = "Prepare the monsoon readiness plan for 2026."
print(f"> {task}")
for update in agent.stream({"messages": [("user", task)]}, stream_mode="updates", subgraphs=True):
    namespace, change = update
    who = "analyst" if namespace else "planner"
    for node, value in change.items():
        for m in (value or {}).get("messages", []) if isinstance(value, dict) else []:
            for call in getattr(m, "tool_calls", None) or []:
                args = {k: (v if len(str(v)) < 70 else str(v)[:67] + "...") for k, v in call["args"].items()}
                print(f"  [{who}] {call['name']}({args})")
print()
print(open("data/plan.md").read())
