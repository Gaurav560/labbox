"""Chapter 15: run with  python main.py"""
from memory import ask, memory_agent

agent = memory_agent()
for member, text in [("M-104", "Hello, I am Ravi. I grow onions and have 40 crates to store."),
                     ("M-104", "How much will storing them cost for 15 days?"),
                     ("M-221", "How much will storing them cost for 15 days?"),
                     ("M-104", "What is my name?")]:
    print(f"[{member}] > {text}\n{ask(agent, member, text)}\n")
