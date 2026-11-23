"""Tools for the two specialist agents: the billing office and the repair office."""
from langchain.tools import tool

READINGS = {"98220": [610, 590, 640, 600, 620, 605, 2410]}
BILLS = {"98220": [("June", 610), ("July", 590), ("August", 2400)]}
VISITS = []


@tool
def meter_readings(phone: str) -> str:
    """Litres a day on this phone's meter for the last seven bills, oldest first."""
    return str(READINGS.get(phone, "no meter found"))


@tool
def recent_bills(phone: str) -> str:
    """The last three bills for this phone, in rupees."""
    return ", ".join(f"{month}: Rs {amount}" for month, amount in BILLS.get(phone, [])) or "no bills found"


@tool
def hold_bill(phone: str, reason: str) -> str:
    """Hold the latest bill until a meter inspector has checked the meter."""
    return f"Bill for {phone} held: {reason}"


@tool
def book_visit(phone: str, problem: str) -> str:
    """Book a repair crew visit for a problem at this phone's address."""
    VISITS.append((phone, problem))
    return f"Visit V-{700 + len(VISITS)} booked for {phone}: {problem}, Thursday 9:00 to 12:00"


BILLING_TOOLS = [meter_readings, recent_bills, hold_bill]
REPAIR_TOOLS = [book_visit]
