"""A photo in the conversation: a member sends a picture of a sick leaf."""
import base64
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

RULES = ("You are Navin, the help desk assistant of a farmers' cooperative. You give a first look at a photo, never a "
         "diagnosis. Never recommend a chemical, a spray or a dose: the next step is always to show the leaf to the "
         "co-op's agronomist, Mrs. Kulkarni.")


class LeafReport(BaseModel):
    """What the photo seems to show. Navin is not an agronomist: a report is a first look, not a diagnosis."""
    crop: str
    problem: str
    confidence: Literal["low", "medium", "high"]
    next_step: str


def image_message(question: str, image: bytes, mime_type: str = "image/jpeg") -> HumanMessage:
    return HumanMessage(content=[
        {"type": "text", "text": question},
        {"type": "image", "base64": base64.b64encode(image).decode(), "mime_type": mime_type},
    ])


def leaf_report(question: str, image: bytes) -> LeafReport:
    model = init_chat_model("openai:ai-chat", temperature=0)
    return model.with_structured_output(LeafReport).invoke([SystemMessage(RULES), image_message(question, image)])
