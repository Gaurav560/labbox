"""Model parameters, and answers that arrive piece by piece."""
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

SYSTEM = "You are Navin, the help desk assistant of the Pimpalgaon Farmers' Cooperative near Nashik. Members grow onions, grapes and tomatoes. Answer in at most three short sentences, in simple words."


def steady_model():
    # TODO (task steady_model): like chapter 7, but also cap the answer: init_chat_model("openai:ai-chat",
    #   temperature=0, max_tokens=120).
    return None


def stream_answer(model, question: str, on_piece) -> str:
    # TODO (task stream_tokens): loop over model.stream([...]) (the system message, then the question); call
    #   on_piece(chunk.content) for every chunk, and return all the pieces joined together.
    return ""
