"""A research team: a planner splits the question, researchers read the board's sources in parallel, a writer
reports with citations, and Python checks every paragraph's citations before the report goes out."""
import operator
import re
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send
from pydantic import BaseModel

SOURCES = Path(__file__).parent / "sources"
PLAN = ("You plan research for the Ujjwal Nagar Water Board. Split the topic into three or four short questions that the "
        "board's own records could answer. The records are: {sources}. Make sure every record that could explain the "
        "topic is covered by a question.")
RESEARCH = ("You research one question using the board's sources. List the sources, read every one that could be "
            "relevant, and answer in two or three sentences with exact facts. Name every source you used.")
CITE = re.compile(r"\[([a-z0-9-]+(?:\s*,\s*[a-z0-9-]+)*)\]")   # [pressure-log] or [pressure-log, field-notes]
WRITE = ("Write a short report for the executive engineer from these findings: four paragraphs at most, then a "
         "recommendation. End every paragraph with its sources in square brackets, like [pressure-log]. Use only the "
         "findings.")


class Plan(BaseModel):
    questions: list[str]


class Finding(BaseModel):
    question: str
    answer: str
    sources: list[str]


class Study(TypedDict, total=False):
    topic: str
    questions: list[str]
    findings: Annotated[list[dict], operator.add]
    report: str
    problems: list[str]
    drafts: int


LIMITER = InMemoryRateLimiter(requests_per_second=0.3, check_every_n_seconds=0.1, max_bucket_size=4)


def model():
    """The chat model, shared limiter included: at most about 18 calls a minute (the gateway allows 20)."""
    return init_chat_model("openai:ai-chat", temperature=0, rate_limiter=LIMITER)


@tool
def list_sources() -> str:
    """The names of the board's sources."""
    return ", ".join(sorted(p.stem for p in SOURCES.glob("*.md")))


@tool
def read_source(name: str) -> str:
    """The full text of one source, by name."""
    path = SOURCES / f"{name}.md"
    return path.read_text() if path.exists() else f"No source called {name}."


def plan(state: Study) -> dict:
    system = SystemMessage(PLAN.format(sources=list_sources.invoke({})))
    return {"questions": model().with_structured_output(Plan).invoke([system, HumanMessage(state["topic"])]).questions}


def fan_out(state: Study) -> list[Send]:
    return [Send("research", {"question": q}) for q in state["questions"]]


def research(task: dict) -> dict:
    agent = create_agent(model(), tools=[list_sources, read_source], system_prompt=RESEARCH, response_format=Finding)
    result = agent.invoke({"messages": [("user", task["question"])]})
    return {"findings": [result["structured_response"].model_dump()]}


def write(state: Study) -> dict:
    notes = "\n\n".join(f"Q: {f['question']}\nA: {f['answer']}\nSources: {', '.join(f['sources'])}" for f in state["findings"])
    if state.get("problems"):
        notes += "\n\nFix these problems in your last draft: " + "; ".join(state["problems"])
    report = model().invoke([SystemMessage(WRITE), HumanMessage(notes)]).content
    return {"report": report, "drafts": state.get("drafts", 0) + 1}


def check_citations(report: str, known: set[str]) -> list[str]:
    """One problem per paragraph that cites no source, or cites a source that does not exist."""
    problems = []
    for paragraph in [p.strip() for p in report.split("\n\n") if p.strip()]:
        if paragraph.startswith("#") or (paragraph.startswith("**") and paragraph.endswith("**")):
            continue  # a title, not a claim
        cited = [name.strip() for group in CITE.findall(paragraph) for name in group.split(",")]
        if not cited:
            problems.append(f"no source: {paragraph[:60]}")
        problems += [f"unknown source [{name}]" for name in cited if name not in known]
    return problems


def review(state: Study) -> Command[Literal["write", "__end__"]]:
    known = {p.stem for p in SOURCES.glob("*.md")}
    problems = check_citations(state["report"], known)
    if problems and state["drafts"] < 2:
        return Command(goto="write", update={"problems": problems})
    return Command(goto=END, update={"problems": problems})


def build_graph():
    graph = StateGraph(Study)
    for name, node in [("plan", plan), ("research", research), ("write", write), ("review", review)]:
        graph.add_node(name, node)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", fan_out, ["research"])
    graph.add_edge("research", "write")
    graph.add_edge("write", "review")
    return graph.compile()
