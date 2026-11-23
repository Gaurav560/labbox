"""Chapter 12: two complaints from the same phone, in two threads, and one from another phone."""
from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore

from chat import Citizen, build_graph

store = InMemoryStore()
app = build_graph(store)
for phone, thread, text in [
    ("98220", "complaint-1", "Please reply in Marathi from now on. No water in Shivaji Nagar since morning."),
    ("98220", "complaint-2", "The pipe near my gate is leaking."),
    ("70300", "complaint-3", "The pipe near my gate is leaking."),
]:
    state = app.invoke({"messages": [("user", text)]}, {"configurable": {"thread_id": thread}}, context=Citizen(phone))
    print(f"{phone} / {thread}\n> {text}\n  {state['messages'][-1].content}\n")
print("stored:", [(item.namespace, item.value) for item in store.search(("citizens",))])

# A store with an index: search crew notes by meaning, not by exact words.
notes = InMemoryStore(index={"embed": init_embeddings("openai:ai-embed"), "dims": 1536})
for key, text in [("n1", "Gandhi Chowk tank: the inlet valve sticks after heavy rain, open it by hand."),
                  ("n2", "Station Road: the main is 40 years old, cast iron, expect bursts in summer."),
                  ("n3", "Old Market: the meter cover on lane 2 is cracked, order a new one.")]:
    notes.put(("crew_notes",), key, {"text": text})
for hit in notes.search(("crew_notes",), query="the tank valve jams in the monsoon", limit=2):
    print(f"{hit.score:.2f}  {hit.value['text']}")
