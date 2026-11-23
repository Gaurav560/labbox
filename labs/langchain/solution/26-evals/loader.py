"""The co-op's rule book as LangChain Documents, cut into pieces small enough to search."""
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_rules(folder: Path) -> list[Document]:
    """One Document per .txt file, in name order, with the file name as its source."""
    return [Document(page_content=path.read_text(), metadata={"source": path.name})
            for path in sorted(folder.glob("*.txt"))]


def split(docs: list[Document], size: int = 300, overlap: int = 30) -> list[Document]:
    """Pieces of at most size characters, overlapping by overlap, each remembering its source and start."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap, add_start_index=True)
    return splitter.split_documents(docs)
