"""Chapter 24: run with  python main.py"""
from agent import navin_agent

agent = navin_agent()
for text in ["My Aadhaar is 4821 3390 1176. Is my membership active?",
             "Please read my whole story. " * 25 + "What should I do?"]:
    result = agent.invoke({"messages": [{"role": "user", "content": text}]})
    shown = text if len(text) < 80 else text[:60] + f"... ({len(text)} characters)"
    print(f"> {shown}")
    print(f"  saved as: {result['messages'][0].content[:70]!r}")
    print(f"  {result['messages'][-1].content}\n")
