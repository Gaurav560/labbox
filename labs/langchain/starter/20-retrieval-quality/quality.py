"""Measuring retrieval: a golden set of questions, each with the rule file that answers it."""
from langchain_core.documents import Document

GOLDEN = [
    ("Can I store 80 crates of onions?", "storage.txt"),
    ("How much loan can I get for 4 acres?", "loans.txt"),
    ("When can I pick grapes after spraying?", "spraying.txt"),
    ("What papers do I need to join?", "membership.txt"),
    ("Who can tell me what is wrong with my vines?", "spraying.txt"),
    ("When will the money from my sale reach me?", "market.txt"),
    ("What does it cost to become a member?", "membership.txt"),
    ("kanda thevaycha aahe, kiti paise lagtil?", "storage.txt"),
]


def hit_rate(sources_for, golden: list[tuple[str, str]], k: int) -> float:
    """The share of golden questions whose expected file is among the first k sources sources_for(question) returns."""
    # TODO (task hit_rate): for each (question, expected) pair, it is a hit when expected is in sources_for(question)[:k].
    #   Return hits / len(golden).
    return 0.0


def titled_chunks(chunks: list[Document], titles: dict[str, str]) -> list[Document]:
    """Each chunk with its document's title in front, so a piece cut from the middle still says what it is about."""
    # TODO (task titled_chunks): for each chunk, look up its document's title in titles (by chunk.metadata["source"]).
    #   Return new Documents with page_content f"{title}: {chunk.page_content}" (unchanged if it already starts with the
    #   title) and a copy of the metadata.
    return chunks
