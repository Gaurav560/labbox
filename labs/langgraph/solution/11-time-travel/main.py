"""Chapter 11: a complaint the rules got wrong, its history, and a correction."""
from ticket import build_graph, correct

app = build_graph()
thread = "C-311"
config = {"configurable": {"thread_id": thread}}
state = app.invoke({"text": "The tap water tastes of rust since the storm."}, config)
print(f"first run: {state['kind']}, {state['severity']} -> {state['reply']}")

print("\nhistory (newest first):")
for snap in app.get_state_history(config):
    print(f"  step {snap.metadata['step']:>2}  {snap.metadata['source']:<6} next={snap.next!s:<14} kind={snap.values.get('kind', '-')}")

state = correct(app, thread, {"kind": "dirty_water", "severity": "urgent"})
print(f"\ncorrected: {state['kind']}, {state['severity']} -> {state['reply']}")

print("\nhistory after the correction (newest first):")
for snap in app.get_state_history(config):
    print(f"  step {snap.metadata['step']:>2}  {snap.metadata['source']:<6} next={snap.next!s:<14} kind={snap.values.get('kind', '-')}")
