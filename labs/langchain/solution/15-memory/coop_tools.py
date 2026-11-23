"""The co-op's tools: facts and arithmetic the model must never guess, as plain Python functions."""
from langchain.tools import tool

RATES = {"onion": 1850, "tomato": 1200, "grapes": 4600}  # rupees per quintal, today


@tool
def mandi_price(crop: str) -> int:
    """Today's mandi rate in rupees per quintal. crop is onion, tomato or grapes."""
    rate = RATES.get(crop.strip().lower())
    if rate is None:
        raise ValueError(f"The co-op has no rate for {crop}: it trades onion, tomato and grapes.")
    return rate


@tool
def storage_cost(crates: int, days: int) -> int:
    """The cold storage charge in rupees for some crates kept some days (Rs 2 per crate per day)."""
    return crates * days * 2
