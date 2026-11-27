"""The first call to a language model, through the LabBox gateway. Run it with: python gateway.py"""
import os

from openai import OpenAI

MODEL = "ai-chat"  # the gateway's name for the model (gpt-4o-mini here); the gateway holds the real key
USD_PER_MILLION_IN = 0.15  # gpt-4o-mini, per 1,000,000 input tokens (the gateway's own price list)
USD_PER_MILLION_OUT = 0.60  # per 1,000,000 output tokens
RS_PER_USD = 88.0  # the rate in Deccan Shield's finance sheet this month
SYSTEM = "You help motor insurance adjusters at Deccan Shield Insurance in Pune. Answer in at most two short sentences."


def client():
    """An OpenAI client pointed at the gateway; LabBox sets both variables in your machine."""
    return OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"], timeout=60, max_retries=2)


def ask(question, openai=None):
    """(answer text, usage) for one question, with SYSTEM as the system message."""
    # TODO (task ask_model): openai = openai or client(). Call openai.chat.completions.create with model=MODEL,
    # temperature=0 and two messages: {"role": "system", "content": SYSTEM} and the user's question. Return the first
    # choice's message.content and the completion's usage.
    return "", None


def cost_rs(usage):
    """What one call cost in rupees: input tokens at the input price, output tokens at the output price."""
    # TODO (task call_cost): usage.prompt_tokens * USD_PER_MILLION_IN plus usage.completion_tokens *
    # USD_PER_MILLION_OUT, divided by 1,000,000 for dollars, times RS_PER_USD for rupees. Do not round here.
    return 0.0


def monthly_rs(usage, calls_per_day, days=30):
    """The cost of calls_per_day such calls every day for `days` days, in rupees, rounded to 2 places."""
    # TODO (task call_cost): cost_rs(usage) * calls_per_day * days, rounded to 2 decimal places.
    return 0.0


if __name__ == "__main__":
    answer, usage = ask("What is a deductible in motor insurance?")
    print(answer)
    print(f"tokens: {usage.prompt_tokens} in, {usage.completion_tokens} out")
    print(f"this call: Rs {cost_rs(usage):.4f}")
    print(f"80 such calls a day for 30 days: Rs {monthly_rs(usage, 80)}")
