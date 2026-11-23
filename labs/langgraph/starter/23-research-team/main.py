"""Chapter 23: one research question for the team; every step is printed, then the report."""
from team import build_graph

topic = "Why have leak complaints on Station Road tripled in 2025, and what should the board do before the monsoon?"
print(f"> {topic}")
report = ""
for update in build_graph().stream({"topic": topic}, stream_mode="updates"):
    for node, change in update.items():
        if node == "plan":
            print("  plan:", *change["questions"], sep="\n    - ")
        elif node == "research":
            f = change["findings"][0]
            print(f"  research: {f['question']}\n    -> {f['answer']}  {f['sources']}")
        elif node == "write":
            report = change["report"]
            print(f"  write: draft {change['drafts']}")
        elif node == "review":
            print(f"  review: {change['problems'] or 'every paragraph cites a real source'}")
print()
print(report)
