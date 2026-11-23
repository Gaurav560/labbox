"""The board's ticket system (a small copy in memory), and the tools Harsh may use on it."""
from langchain.tools import tool

TICKETS = {
    "T-4471": {"phone": "98220", "street": "Tilak Nagar, lane 3", "kind": "no_water", "opened": "Monday 9:10",
               "status": "crew assigned", "crew": "East zone crew 2", "visit": "Wednesday 8:00 to 11:00"},
    "T-4475": {"phone": "98220", "street": "Tilak Nagar, lane 3", "kind": "dirty_water", "opened": "Tuesday 21:40",
               "status": "water sample taken", "crew": "health team", "visit": "lab result by Wednesday 18:00"},
    "T-4480": {"phone": "70300", "street": "Station Road", "kind": "leak", "opened": "Tuesday 7:55",
               "status": "waiting for parts", "crew": "South zone crew 1", "visit": "not booked yet"},
}


@tool
def find_tickets(phone: str) -> str:
    """List the open complaint tickets for a citizen's phone number."""
    found = [f"{tid}: {t['kind']} at {t['street']}, opened {t['opened']}" for tid, t in TICKETS.items() if t["phone"] == phone]
    return "\n".join(found) or f"No open tickets for {phone}."


@tool
def ticket_status(ticket_id: str) -> str:
    """The current status of one ticket: what was done, who has it, and when they visit."""
    t = TICKETS.get(ticket_id.strip().upper())
    if not t:
        return f"No ticket {ticket_id}."
    return f"{ticket_id}: {t['status']}; {t['crew']}; {t['visit']}"


TOOLS = [find_tickets, ticket_status]
