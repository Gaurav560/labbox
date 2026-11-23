"""Chapter 10: start repairs, then answer as the engineer, in separate runs.

    python main.py start <job> "<work>" "<street>" <estimate>
    python main.py decide <job> yes|no "<note>"
"""
import sys

from repair import build_graph, decide, open_saver

app = build_graph(open_saver())
command, job = sys.argv[1], sys.argv[2]
if command == "start":
    work, street, estimate = sys.argv[3], sys.argv[4], int(sys.argv[5])
    state = app.invoke({"job": job, "work": work, "street": street, "estimate": estimate},
                       {"configurable": {"thread_id": job}})
else:
    state = decide(app, job, sys.argv[3] == "yes", sys.argv[4])
if "__interrupt__" in state:
    asked = state["__interrupt__"][0].value
    print(f"{job} is waiting for the engineer: Rs {asked['estimate']:,}")
    print(f"  brief: {asked['brief']}")
else:
    print(f"{job}: {state['status']}")
