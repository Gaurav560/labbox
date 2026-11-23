"""The billing office's own graph: load a meter's readings and decide whether the bill is right."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

READINGS = {  # litres a day, the last seven bills, oldest first
    "98220": [610, 590, 640, 600, 620, 605, 2410],
    "70300": [380, 410, 395, 400, 420, 390, 405],
}


class Bill(TypedDict, total=False):
    phone: str
    readings: list[int]
    verdict: str


def load_readings(state: Bill) -> dict:
    return {"readings": READINGS.get(state["phone"], [])}


def check_jump(state: Bill) -> dict:
    *before, last = state["readings"]
    average = sum(before) / len(before)
    if last > 3 * average:
        return {"verdict": f"held: {last} litres a day against an average of {average:.0f}; a meter inspector will visit"}
    return {"verdict": f"correct: {last} litres a day, close to the average of {average:.0f}"}


def build_billing():
    graph = StateGraph(Bill)
    graph.add_node("load_readings", load_readings)
    graph.add_node("check_jump", check_jump)
    graph.add_edge(START, "load_readings")
    graph.add_edge("load_readings", "check_jump")
    graph.add_edge("check_jump", END)
    return graph.compile()
