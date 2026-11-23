"""Chapter 13: a citizen asks about their complaints; every step of the agent loop is printed."""
from agent import build_graph

app = build_graph()
config = {"configurable": {"thread_id": "98220"}}
for text in ["Any update on my complaints?", "98220", "Is the brown water safe to drink until the result comes?"]:
    print(f"> {text}")
    for update in app.stream({"messages": [("user", text)]}, config, stream_mode="updates"):
        for node, change in update.items():
            for m in change["messages"]:
                if m.type == "ai" and m.tool_calls:
                    print(f"  [{node}] asks for " + ", ".join(f"{c['name']}({c['args']})" for c in m.tool_calls))
                elif m.type == "tool":
                    print(f"  [{node}] {m.name} -> " + m.content.replace("\n", " | "))
                else:
                    print(f"  [{node}] {m.content}")
