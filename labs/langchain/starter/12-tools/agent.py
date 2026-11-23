"""Navin with the member tools. The app says who is asking, through the context."""
from langchain.agents import create_agent

from coop_tools import mandi_price, storage_cost
from member_tools import Member, crop_loan_limit, my_storage

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words. Use your tools for rates and charges; never calculate or guess them yourself."


def navin_agent():
    return create_agent("openai:ai-chat", tools=[mandi_price, storage_cost, crop_loan_limit, my_storage],
                        system_prompt=SYSTEM, context_schema=Member)
