"""Chapter 11: run with  python main.py"""
from agent import navin_agent, tools_used

agent = navin_agent()
for question in ["What does it cost to keep 25 crates of tomatoes for a week?", "What is the garlic rate today?"]:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print(f"> {question}\n{result['messages'][-1].content}\n  tools: {tools_used(result)}, {len(result['messages'])} messages\n")
