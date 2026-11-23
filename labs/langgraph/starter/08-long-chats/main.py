"""Chapter 8: the same six messages, sent to a trimming Harsh and a summarising Harsh."""
from chat import build_summarised, build_trimmed

CHAT = [
    "Hello, this is Sunita Pawar, 14 Tilak Nagar, lane 3. No water since Monday.",
    "Is it the whole area or only our lane?",
    "The neighbours say a tanker came yesterday, but not to lane 3.",
    "Can the tanker come after 6 in the evening? I work during the day.",
    "One more thing: the meter outside is also dripping.",
    "Please read back my address and the time I asked for.",
]

for name, app in [("trimmed", build_trimmed()), ("summarised", build_summarised())]:
    print(f"=== {name}")
    config = {"configurable": {"thread_id": name}}
    for text in CHAT:
        state = app.invoke({"messages": [("user", text)]}, config)
        answer = [m for m in state["messages"] if m.type == "ai"][-1]
        print(f"> {text}")
        print(f"  {answer.content}  [{answer.usage_metadata['input_tokens']} tokens in, {len(state['messages'])} kept]")
    if state.get("summary"):
        print(f"summary: {state['summary']}")
