"""Chapter 1: run with  python main.py"""
from graph import build_graph, steps

graph = build_graph()
for text in ["The water from our tap is brown and smells bad.", "There is no water in Gandhi Chowk since morning.",
             "My bill shows 900 litres a day, we are two people."]:
    print(f"> {text}")
    print(f"  {graph.invoke({'text': text})}")
print("\nsteps:", steps("Pipe burst near the school"))
print()
print(graph.get_graph().draw_mermaid())
