"""What a model really reads: tokens, counted with the tokenizer OpenAI's gpt-4o models use (o200k_base)."""
import tiktoken

ENCODING = tiktoken.get_encoding("o200k_base")


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def pieces(text: str) -> list[str]:
    """The text cut into its tokens, each decoded back to text."""
    return [ENCODING.decode([t]) for t in ENCODING.encode(text)]


def fit_window(messages: list[str], budget: int) -> list[str]:
    kept, used = [], 0
    for message in reversed(messages):
        cost = count_tokens(message)
        if used + cost > budget:
            break
        kept.append(message)
        used += cost
    return list(reversed(kept))
