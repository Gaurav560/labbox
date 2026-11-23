"""Chapter 16: three tickets through the desk graph, with every step of every subgraph."""
from desk import build_graph

app = build_graph()
for ticket in [{"ticket": "T-4490", "phone": "98220", "text": "My bill is Rs 2,400, usually Rs 600."},
               {"ticket": "T-4491", "phone": "70300", "text": "The meter bill looks high this month."},
               {"ticket": "T-4492", "phone": "70300", "text": "Pipe burst outside the school gate."}]:
    print(f"> {ticket['ticket']}: {ticket['text']}")
    for namespace, update in app.stream(ticket, stream_mode="updates", subgraphs=True):
        where = namespace[0].split(":")[0] + " / " if namespace else ""
        print(f"  {where}{update}")
    print()
