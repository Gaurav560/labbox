"""Model parameters, and answers that arrive piece by piece."""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def steady_model():
    return init_chat_model("openai:ai-chat", temperature=0, max_tokens=120)


def stream_answer(model, question: str, on_piece) -> str:
    pieces = []
    for chunk in model.stream([SystemMessage(SYSTEM), HumanMessage(question)]):
        on_piece(chunk.content)
        pieces.append(chunk.content)
    return "".join(pieces)
