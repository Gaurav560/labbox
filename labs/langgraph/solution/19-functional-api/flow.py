"""The repair job again, as plain Python functions: @task steps are saved, @entrypoint makes it durable."""
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt

import board

APPROVAL_OVER = 50_000
saver = SqliteSaver(sqlite3.connect("jobs.db", check_same_thread=False))


@task
def book_crew(job: str) -> str:
    return board.book_crew(job)


@task
def order_parts(job: str) -> str:
    return board.order_parts(job)


@task
def send_sms(job: str) -> str:
    return board.send_sms(job)


@entrypoint(checkpointer=saver)
def repair_job(order: dict) -> list[str]:
    job = order["job"]
    if order["estimate"] > APPROVAL_OVER:
        decision = interrupt({"job": job, "estimate": order["estimate"], "question": "Approve this repair?"})
        if not decision["approve"]:
            return [f"{job}: refused ({decision.get('note', '')})"]
    log = [book_crew(job).result(), order_parts(job).result()]
    log.append(send_sms(job).result())
    return log
