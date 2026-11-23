"""The repair job again, as plain Python functions: @task steps are saved, @entrypoint makes it durable."""
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt

import board

APPROVAL_OVER = 50_000
saver = SqliteSaver(sqlite3.connect("jobs.db", check_same_thread=False))


# TODO (task task_steps): put @task above each of these three functions, so each call's result is saved in the
#   checkpoint; then in repair_job, call each one and take its .result() (a @task call returns a future).
def book_crew(job: str) -> str:
    return board.book_crew(job)


def order_parts(job: str) -> str:
    return board.order_parts(job)


def send_sms(job: str) -> str:
    return board.send_sms(job)


@entrypoint(checkpointer=saver)
def repair_job(order: dict) -> list[str]:
    job = order["job"]
    # TODO (task approval_in_flow): over APPROVAL_OVER, ask with interrupt({"job": job, "estimate": order["estimate"],
    #   "question": "Approve this repair?"}); if the answer's "approve" is false, return [f"{job}: refused (<note>)"].
    log = [book_crew(job), order_parts(job)]
    log.append(send_sms(job))
    return log
