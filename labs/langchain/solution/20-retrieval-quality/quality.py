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
    hits = sum(1 for question, expected in golden if expected in sources_for(question)[:k])
    return hits / len(golden)


def titled_chunks(chunks: list[Document], titles: dict[str, str]) -> list[Document]:
    """Each chunk with its document's title in front, so a piece cut from the middle still says what it is about."""
    out = []
    for chunk in chunks:
        title = titles[chunk.metadata["source"]]
        text = chunk.page_content if chunk.page_content.startswith(title) else f"{title}: {chunk.page_content}"
        out.append(Document(page_content=text, metadata=dict(chunk.metadata)))
    return out
