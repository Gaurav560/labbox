"""Chapter 9: run a repair job; if it crashes, run the same command again.

    python main.py <job id>          (SMS_FAILS=<n> python main.py ... makes the SMS gateway fail n times)
"""
import sys

from job import open_saver, run_job, build_graph

job = sys.argv[1]
app = build_graph(open_saver())
config = {"configurable": {"thread_id": job}}
waiting = app.get_state(config).next
print(f"{job}: " + (f"continuing at {waiting[0]}" if waiting else "starting"))
try:
    state = run_job(app, job)
    print("done:", *state["log"], sep="\n  ")
except Exception as e:
    print(f"crashed: {type(e).__name__}: {e}")
    print(f"saved: next step is {app.get_state(config).next}")
