"""Chapter 4: run with  python main.py"""
from graph import build_graph

graph = build_graph()
for text in ["Tap water in Tilak Nagar smells like sewage, my children drank it.",
             "Since 3 days no water in the upper floors of Station Road society.",
             "Why is my bill Rs 2,400 this month? Usually it is Rs 600.",
             "pani nahi aaya aaj gandhi chowk mein"]:
    final = graph.invoke({"text": text})
    print(f"> {text}\n  {final['kind']}, {final['severity']}, street {final['street']!r}\n  {final['reply']}\n")
