"""Chapter 12: run with  python main.py"""
from agent import navin_agent
from member_tools import Member, crop_loan_limit, my_storage

print(crop_loan_limit.name, "|", crop_loan_limit.description, "|", crop_loan_limit.args)
agent = navin_agent()
for member, question in [("M-104", "How many crates do I have in storage, and how much loan can I get for 2.5 acres?"),
                         ("M-221", "How many crates do I have in storage?")]:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, context=Member(member))
    print(f"\n[{member}] > {question}\n{result['messages'][-1].content}")
