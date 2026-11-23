"""Chapter 14: one question per run (a run can make up to 12 model calls); every check is printed.

    python main.py "<question>"
"""
import sys

from reflection import build_graph

app = build_graph()
text = sys.argv[1] if len(sys.argv) > 1 else "My number is 98220. When will my water come back?"
config = {"configurable": {"thread_id": "one"}}
print(f"> {text}")
for update in app.stream({"messages": [("user", text)]}, config, stream_mode="updates"):
    for node, change in update.items():
        for m in (change or {}).get("messages", []):
            if node == "agent" and not m.tool_calls:
                print(f"  draft: {m.content}")
            elif node == "check_answer":
                print(f"  checker: {m.content}")
print(f"  SENT: {app.get_state(config).values['messages'][-1].content}")
