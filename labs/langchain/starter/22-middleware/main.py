"""Chapter 22: run with  python main.py"""
from agent import navin_agent

agent = navin_agent()
config = {"configurable": {"thread_id": "M-104"}}
turns = ["Please look up today's garlic rate with your tool.", "Hello, I am Ravi. I grow onions in Lasalgaon.",
         "What is the onion rate today?", "And what does storing 40 crates for 10 days cost?", "And for 20 days?",
         "Thank you. What did I say I grow?"]
for text in turns:
    result = agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
    print(f"> {text}\n{result['messages'][-1].content}")
    print(f"  ({len(result['messages'])} messages kept in the thread)\n")
first = agent.get_state(config).values["messages"][0]
print("the thread now starts with:", type(first).__name__, repr(first.content[:160]))
