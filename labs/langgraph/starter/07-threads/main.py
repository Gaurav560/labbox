"""Chapter 7: one message per run, like a real WhatsApp desk.

    python main.py <phone> "<message>"

Each run is a new process: the conversation survives only because the checkpointer keeps it in harsh.db.
"""
import sys

from chat import ask, build_graph, open_saver

phone, text = sys.argv[1], sys.argv[2]
app = build_graph(open_saver("harsh.db"))
print(f"Harsh: {ask(app, phone, text)}")
saved = app.get_state({"configurable": {"thread_id": phone}}).values["messages"]
print(f"({len(saved)} messages saved in thread {phone})")
