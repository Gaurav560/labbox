"""A repair job that survives a crash: every finished step is saved, and never done twice."""
import operator
import sqlite3
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

import board
from board import SmsTimeout


class Job(TypedDict, total=False):
    job: str
    log: Annotated[list[str], operator.add]


def book_crew(state: Job) -> dict:
    return {"log": [board.book_crew(state["job"])]}


def order_parts(state: Job) -> dict:
    return {"log": [board.order_parts(state["job"])]}


def notify_citizen(state: Job) -> dict:
    return {"log": [board.send_sms(state["job"])]}


def build_graph(checkpointer):
    graph = StateGraph(Job)
    graph.add_node("book_crew", book_crew)
    graph.add_node("order_parts", order_parts)
    graph.add_node("notify_citizen", notify_citizen,
                   retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.5, retry_on=SmsTimeout))
    graph.add_edge(START, "book_crew")
    graph.add_edge("book_crew", "order_parts")
    graph.add_edge("order_parts", "notify_citizen")
    graph.add_edge("notify_citizen", END)
    return graph.compile(checkpointer=checkpointer)


def run_job(app, job: str) -> dict:
    """Start the job, or, if it stopped part-way, continue it from its last checkpoint."""
    config = {"configurable": {"thread_id": job}}
    if app.get_state(config).next:
        return app.invoke(None, config)
    return app.invoke({"job": job}, config)


def open_saver(path: str = "jobs.db") -> SqliteSaver:
    return SqliteSaver(sqlite3.connect(path, check_same_thread=False))
