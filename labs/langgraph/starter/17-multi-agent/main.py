"""Chapter 17: one message with two problems, and the specialists that handle them."""
from team import build_graph

text = "My number is 98220. My August bill is Rs 2,400 instead of about Rs 600, and the meter outside is dripping."
print(f"> {text}")
state = build_graph().invoke({"messages": [("user", text)]})
for m in state["messages"][1:]:
    print(f"  [{m.name}] {m.content}")
