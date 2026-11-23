"""Tests for the desk graph. Run them with:  python -m pytest -v"""
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from desk import build_graph


def fake_llm():
    """A chat model that answers from a list, with no network and no cost."""
    return GenericFakeChatModel(messages=iter([AIMessage("We have your complaint and will reply soon.")] * 5))


def test_small_repair_is_scheduled():  # a worked example
    state = build_graph(fake_llm()).invoke({"text": "Pipe leaking near the gate", "estimate": 1200})
    assert state["team"] == "repair crew"
    assert state["reply"] == "We have your complaint and will reply soon."


def test_dirty_water_goes_to_health():
    state = build_graph(fake_llm()).invoke({"text": "Brown water from the tap", "estimate": 0})
    assert state["kind"] == "dirty_water"
    assert state["team"] == "health team"


def test_big_repair_waits_for_engineer():
    app = build_graph(fake_llm(), checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "J-1"}}
    state = app.invoke({"text": "Pipe burst on Station Road", "estimate": 65000}, config)
    assert state["__interrupt__"][0].value["estimate"] == 65000
    assert app.get_state(config).next == ("approval",)
    state = app.invoke(Command(resume={"approve": False, "note": "no budget"}), config)
    assert state["status"] == "refused: no budget"
    assert "reply" not in state
