"""Chapter 3: run with  python main.py"""
from graph import build_graph

graph = build_graph()
for text, street in [("Brown water from the tap", "Gandi Chowk"), ("No water since morning", "Station Road"),
                     ("Bill is double this month", "tilaknagar"), ("Pipe leaking", "Shivaji Path")]:
    final = graph.invoke({"text": text, "street": street})
    print(f"> {text} ({street}): {final['kind']}, tries {final['tries']} -> {final['team']}")
print()
print(graph.get_graph().draw_mermaid())
