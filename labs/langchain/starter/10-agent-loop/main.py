"""Chapter 10: run with  python main.py"""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

from coop_tools import mandi_price, storage_cost
from loop import agent_loop

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."

model = init_chat_model("openai:ai-chat", temperature=0)
messages = [SystemMessage(SYSTEM), HumanMessage("What is today's onion rate, and what does it cost to store 60 crates for 10 days?")]
answer = agent_loop(model, messages, [mandi_price, storage_cost])
for m in messages:
    calls = getattr(m, "tool_calls", None)
    print(f"{type(m).__name__:14}", calls if calls else repr(m.content)[:110])
