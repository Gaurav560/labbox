"""Chapter 15: one question per run; every step of the RAG loop is printed.

    python main.py "<question>"
"""
import sys

from rag import build_graph

text = sys.argv[1] if len(sys.argv) > 1 else "Our water has been off since Monday. Do we have to pay for a tanker?"
print(f"> {text}")
for update in build_graph().stream({"messages": [("user", text)]}, stream_mode="updates"):
    for node, change in update.items():
        m = change["messages"][-1]
        if m.type == "ai" and m.tool_calls:
            print(f"  [{node}] search: {m.tool_calls[0]['args']['query']}")
        elif m.type == "tool":
            print(f"  [{node}] found: " + m.content.replace("\n\n", " || ")[:150] + "...")
        else:
            print(f"  [{node}] {m.content}")
