"""Chapter 19: run with  python main.py"""
from rag import rag_agent

agent = rag_agent()
for question in ["Can I store 80 crates of onions? How long until I know?", "I sprayed my grapes on Monday. Can I harvest on Friday?",
                 "Do you give loans for buying a tractor?"]:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print(f"> {question}\n{result['messages'][-1].content}\n")
