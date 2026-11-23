"""Booking cold storage: a tool that changes something, so a person checks it first (chapter 25)."""
from langchain.tools import tool

BOOKINGS: list[dict] = []


@tool
def book_storage(crates: int, days: int, crop: str) -> str:
    """Book cold storage for the member: crates, days, and the crop (onion, tomato or grapes)."""
    BOOKINGS.append({"crates": crates, "days": days, "crop": crop})
    return f"Booked {crates} crates of {crop} for {days} days, number B-{100 + len(BOOKINGS)}."
