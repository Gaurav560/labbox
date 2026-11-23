"""Chapter 23: run with  python main.py"""
from agent import AUDIT, Member, navin_agent

agent = navin_agent()
for member in [Member("M-104", "Ravi", "Marathi"), Member("M-221", "Asha", "English")]:
    result = agent.invoke({"messages": [{"role": "user", "content": "What does storing 25 crates for 8 days cost?"}]},
                          context=member)
    print(f"[{member.name}, {member.language}] {result['messages'][-1].content}\n")
print("audit log:")
for line in AUDIT:
    print("  ", line)
