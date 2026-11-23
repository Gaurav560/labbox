"""Chapter 2: run with  python main.py"""
from graph import build_graph

graph = build_graph()
for text in ["Small leak in the lane behind the school.", "Brown water near the district hospital.", "Meter reading looks wrong."]:
    final = graph.invoke({"text": text})
    print(f"> {text}\n  severity {final['severity']}, log {final['log']}")
