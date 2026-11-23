"""Chapter 13: run with  python main.py"""
from booking import booking_agent, extract_booking

for message in ["Please keep 60 crates of kanda for two weeks", "tomatoes, 25 kreats, till next monday", "Store my garlic, 10 crates, 5 days"]:
    try:
        print(f"{message!r:55} -> {extract_booking(message)!r}")
    except Exception as e:
        print(f"{message!r:55} -> {type(e).__name__}: {str(e).splitlines()[0]}")

result = booking_agent().invoke({"messages": [{"role": "user", "content": "I want to store 40 crates of grapes for 3 days"}]})
print("\nagent:", repr(result["structured_response"]), [type(m).__name__ for m in result["messages"]])
