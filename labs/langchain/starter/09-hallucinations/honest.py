"""A model that invents an answer is worse than no answer. And every answer has a price."""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."
FACTS = """Pimpalgaon Farmers' Cooperative, facts valid from 1 November:
- Office: Monday to Saturday, 9:00 to 17:00. Closed on Sundays.
- Today's mandi rates, per quintal: onion Rs 1,850, tomato Rs 1,200, grapes Rs 4,600.
- Cold storage: Rs 2 per crate per day. Bookings of more than 50 crates need the manager's approval.
- Crop loans: up to Rs 50,000 per acre, at 7% a year.
- Co-op rule: no grape harvest for 10 days after any fungicide spray.
"""

# gpt-4o-mini, in US dollars per million tokens
INPUT_PER_MILLION = 0.15
OUTPUT_PER_MILLION = 0.60


def honest_prompt() -> str:
    # TODO (task honest_prompt): return SYSTEM, then an instruction: if the answer is not in the facts, say
    #   "I don't know" and suggest calling the co-op office; never invent prices, dates or rules. Then a blank line,
    #   "Facts:" and FACTS. Your text must contain the words "I don't know" and every line of FACTS.
    return SYSTEM


def ask(question: str):
    model = init_chat_model("openai:ai-chat", temperature=0)
    return model.invoke([SystemMessage(honest_prompt()), HumanMessage(question)])


def answer_cost(reply) -> float:
    # TODO (task answer_cost): reply.usage_metadata has "input_tokens" and "output_tokens". Return the price of the
    #   reply in dollars: input tokens times INPUT_PER_MILLION, plus output tokens times OUTPUT_PER_MILLION,
    #   divided by one million.
    return 0.0
