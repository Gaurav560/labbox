"""What a model really reads: tokens, counted with the tokenizer OpenAI's gpt-4o models use (o200k_base)."""
import tiktoken

ENCODING = tiktoken.get_encoding("o200k_base")


def count_tokens(text: str) -> int:
    # TODO (task count_tokens): return how many tokens the text is: ENCODING.encode(text) gives the list of token ids.
    return 0


def pieces(text: str) -> list[str]:
    """The text cut into its tokens, each decoded back to text."""
    return [ENCODING.decode([t]) for t in ENCODING.encode(text)]


def fit_window(messages: list[str], budget: int) -> list[str]:
    # TODO (task fit_window): keep the NEWEST messages whose tokens together fit in the budget, and return them in
    #   their original order. Walk from the last message backwards; stop at the first one that does not fit.
    return messages
