"""LangChain: one interface for every chat model, and messages as objects."""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def chat_model():
    # TODO (task chat_model): return init_chat_model("openai:ai-chat", temperature=0).
    #   It reads OPENAI_BASE_URL and OPENAI_API_KEY from the environment, like the SDK did.
    return None


def ask(model, question: str) -> str:
    # TODO (task system_message): call model.invoke([...]) with a SystemMessage(SYSTEM) and a HumanMessage(question),
    #   and return the reply's .content.
    return ""
