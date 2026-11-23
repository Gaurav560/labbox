"""Chapter 18: what a chat screen would show, with the time of every event."""
import time

from stream import build_graph, events

start = time.perf_counter()
tokens = 0
for kind, text in events(build_graph(), "98220"):
    at = time.perf_counter() - start
    if kind == "progress":
        print(f"[{at:4.2f}s] ... {text}")
    else:
        tokens += 1
        if tokens == 1:
            print(f"[{at:4.2f}s] first token")
        print(text, end="|", flush=True)
print(f"\n[{time.perf_counter() - start:4.2f}s] done, {tokens} chunks")
