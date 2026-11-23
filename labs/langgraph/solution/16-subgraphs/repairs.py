"""The repair office's own graph (the job of chapter 9, without the database): its state speaks of jobs, not tickets."""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class Job(TypedDict, total=False):
    job: str
    log: Annotated[list[str], operator.add]


def book_crew(state: Job) -> dict:
    return {"log": [f"{state['job']}: crew booked"]}


def order_parts(state: Job) -> dict:
    return {"log": [f"{state['job']}: parts ordered"]}


def build_repairs():
    graph = StateGraph(Job)
    graph.add_node("book_crew", book_crew)
    graph.add_node("order_parts", order_parts)
    graph.add_edge(START, "book_crew")
    graph.add_edge("book_crew", "order_parts")
    graph.add_edge("order_parts", END)
    return graph.compile()
