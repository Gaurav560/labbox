"""The co-op's rule book as LangChain Documents, cut into pieces small enough to search."""
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_rules(folder: Path) -> list[Document]:
    """One Document per .txt file, in name order, with the file name as its source."""
    # TODO (task load_rules): for every .txt file in folder (sorted(folder.glob("*.txt"))), make a
    #   Document(page_content=<the file's text>, metadata={"source": <the file's name>}). Return them in a list.
    return []


def split(docs: list[Document], size: int = 300, overlap: int = 30) -> list[Document]:
    """Pieces of at most size characters, overlapping by overlap, each remembering its source and start."""
    # TODO (task split_rules): make a RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap,
    #   add_start_index=True) and return splitter.split_documents(docs).
    return docs
