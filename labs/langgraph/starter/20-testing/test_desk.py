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
    # TODO (task test_routes): run build_graph(fake_llm()) on a dirty-water complaint ("Brown water from the tap",
    #   estimate 0), then assert that kind is "dirty_water" and team is "health team".
    pass


def test_big_repair_waits_for_engineer():
    # TODO (task test_interrupts): build the graph with checkpointer=InMemorySaver(), invoke a Rs 65,000 repair with
    #   a thread id, assert it paused (state["__interrupt__"], and app.get_state(config).next == ("approval",)),
    #   resume with Command(resume={"approve": False, "note": "no budget"}), and assert the status is
    #   "refused: no budget" and no reply was written.
    pass
