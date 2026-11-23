"""Chapter 19: run repair jobs written with the Functional API.

    python main.py start <job> <estimate>     (SMS_FAILS=<n> makes the SMS gateway fail n times)
    python main.py resume <job>
    python main.py decide <job> yes|no "<note>"
"""
import sys

from langgraph.types import Command

from flow import repair_job

command, job = sys.argv[1], sys.argv[2]
config = {"configurable": {"thread_id": job}}
if command == "start":
    run = {"job": job, "estimate": int(sys.argv[3])}
elif command == "resume":
    run = None
else:
    run = Command(resume={"approve": sys.argv[3] == "yes", "note": sys.argv[4]})
try:
    for update in repair_job.stream(run, config, stream_mode="updates"):
        for name, value in update.items():
            print(f"  {name}: {value}")
except Exception as e:
    print(f"crashed: {type(e).__name__}: {e}")
