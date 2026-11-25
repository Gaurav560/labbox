"""Chapter 5: run with  python main.py"""
from graph import build_notice_loop, build_parallel

parallel = build_parallel()
for street in ["Station Road", "Tilak Nagar"]:
    print(f"{street}: {parallel.invoke({'street': street})}")
    print("  steps:", [list(u) for u in parallel.stream({"street": street}, stream_mode="updates")])

print()
facts = "Old Market and Tilak Nagar; Thursday 3 December; 10:00 to 16:00; replacing the valve at the Tilak Nagar tank"
for update in build_notice_loop().stream({"facts": facts}, stream_mode="updates"):
    for node, data in update.items():
        if node == "write_notice":
            print(f"--- draft {data['drafts']}:\n{data['draft']}")
        else:
            print(f"--- grade: good={data['good']} {data['feedback']}")
