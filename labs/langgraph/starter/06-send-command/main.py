"""Chapter 6: run with  python main.py"""
from graph import build_repair_graph, build_storm_graph

night = ["Pipe burst outside the bakery on Station Road", "No water in Tilak Nagar since the storm",
         "Brown water in Old Market", "Leak at the Gandhi Chowk tank", "Meter cover broken, bill looks wrong"]
final = build_storm_graph().invoke({"complaints": night})
for ticket in final["tickets"]:
    print(f"  {ticket['severity']:7} {ticket['kind']:12} Rs {ticket['estimate']:>6,}  {ticket['text']}")
print(final["summary"])

repairs = build_repair_graph()
for ticket in final["tickets"]:
    if ticket["estimate"]:
        print(f"\n{ticket['kind']}, Rs {ticket['estimate']:,}: {repairs.invoke(ticket)['status']}")
