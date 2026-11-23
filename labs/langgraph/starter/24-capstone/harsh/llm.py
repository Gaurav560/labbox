"""One chat model for the whole app, with a shared rate limiter (the gateway allows 20 calls a minute)."""
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

LIMITER = InMemoryRateLimiter(requests_per_second=0.3, check_every_n_seconds=0.1, max_bucket_size=4)


def model():
    return init_chat_model("openai:ai-chat", temperature=0, rate_limiter=LIMITER)
