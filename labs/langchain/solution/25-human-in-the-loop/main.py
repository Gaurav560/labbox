"""Chapter 25: run with  python main.py"""
from agent import booking_agent, manager_decides
from booking import BOOKINGS

agent = booking_agent()
cases = [("M-104", "Please book 80 crates of onions for 10 days.", {"type": "edit", "edited_action": {"name": "book_storage", "args": {"crates": 50, "days": 10, "crop": "onion"}}}),
         ("M-221", "Book 20 crates of tomatoes for 5 days, please.", {"type": "approve"}),
         ("M-305", "Book 300 crates of grapes for 2 days.", {"type": "reject", "message": "The grape chamber is full this week."})]
for member, text, decision in cases:
    config = {"configurable": {"thread_id": member}}
    result = agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
    request = result["__interrupt__"][0].value["action_requests"][0]
    print(f"[{member}] > {text}\n  paused, waiting for the manager: {request['name']} {request['args']}")
    print(f"  the manager decides: {decision['type']}")
    result = manager_decides(agent, member, decision)
    print(f"  {result['messages'][-1].content}\n")
print("bookings made:", BOOKINGS)
