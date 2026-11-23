"""Guardrails: a member's Aadhaar number never reaches the model, and over-long messages never reach it at all."""
import re

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, before_agent
from langchain.messages import AIMessage

from coop_tools import mandi_price, storage_cost

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."
MAX_CHARS = 500
TOO_LONG = "That message is too long for me. Please ask in a few sentences, or call the co-op office."

# An Aadhaar number: 12 digits, the first 2 to 9, often written in groups of four.
AADHAAR = re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b")


def find_aadhaar(text: str) -> list[dict]:
    """Every Aadhaar number in the text, as PII matches: type, value, start and end."""
    return [{"type": "aadhaar", "value": m.group(), "start": m.start(), "end": m.end()} for m in AADHAAR.finditer(text)]


@before_agent(can_jump_to=["end"])
def length_guard(state, runtime):
    """Runs once, before the agent starts: a message over MAX_CHARS gets a polite refusal and no model call."""
    if len(state["messages"][-1].content) > MAX_CHARS:
        return {"messages": [AIMessage(TOO_LONG)], "jump_to": "end"}
    return None


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost], system_prompt=SYSTEM,
                        middleware=[length_guard,
                                    PIIMiddleware("aadhaar", detector=find_aadhaar, strategy="mask", apply_to_input=True)])
