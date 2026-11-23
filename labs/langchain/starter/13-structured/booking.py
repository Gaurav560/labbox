"""Answers as Python objects: a free-text request becomes a Booking the co-op's code can use."""
from typing import Literal

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field


class Booking(BaseModel):
    """A cold storage booking request."""
    crop: Literal["onion", "tomato", "grapes"]
    crates: int = Field(description="number of crates, 1 or more")
    days: int = Field(description="how many days to store them")


def extract_booking(message: str) -> Booking:
    model = init_chat_model("openai:ai-chat", temperature=0)
    # TODO (task extract_booking): return model.with_structured_output(Booking).invoke(message): the model's answer,
    #   parsed and checked into a Booking.
    return None


def booking_agent():
    # TODO (task booking_agent): return create_agent("openai:ai-chat", tools=[], response_format=Booking), so a run
    #   ends with result["structured_response"], a Booking.
    return None
