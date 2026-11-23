"""More tools: one with a calculation the co-op must get right, one that knows who is asking."""
from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool

# The co-op's records: member id -> (name, acres farmed, crates in cold storage)
MEMBERS = {"M-104": ("Ravi Patil", 3.0, 40), "M-221": ("Asha Shinde", 1.5, 0)}


@dataclass
class Member:
    """Who is asking: given by the app, never by the model."""
    member_id: str


@tool
def crop_loan_limit(acres: float) -> int:
    """The most crop loan in rupees a member can get for some acres (Rs 50,000 per acre)."""
    return int(acres * 50000)


@tool
def my_storage(runtime: ToolRuntime[Member]) -> str:
    """How many crates the member who is asking has in cold storage."""
    name, _, crates = MEMBERS[runtime.context.member_id]
    return f"{name} has {crates} crates in cold storage."
