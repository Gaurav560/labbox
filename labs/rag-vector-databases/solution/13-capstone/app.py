"""Chapter 13: Fieldbook as a web service. Run with  uvicorn app:app --port 8000  and, in a second terminal,
curl "localhost:8000/search?q=leopard+in+a+village&kind=report"   or   curl -X POST localhost:8000/ask -d ..."""
from functools import lru_cache

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

from fieldbook import Index, answer, load_corpus, rerank

app = FastAPI(title="Fieldbook")


@lru_cache(maxsize=1)
def index():
    """Built once, on the first request: every chunk embedded and tokenized (a few seconds)."""
    return Index(load_corpus())


@lru_cache(maxsize=1)
def client():
    return OpenAI()


def find(q, kind=None, zone=None, k=5):
    """Two-stage search over the chunks that match the filters: hybrid for 20 candidates, then reranked to k."""
    full = index()
    allowed = {c["id"] for c in full.chunks if (kind is None or c["kind"] == kind) and (zone is None or c["zone"] == zone)}
    candidates = [c for c in full.hybrid(q, k=len(full.chunks)) if c["id"] in allowed][:20]
    return rerank(q, candidates, top_n=k) if candidates else []


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search")
def search(q: str, kind: str | None = None, zone: str | None = None, k: int = 5):
    return {"query": q, "results": [{"id": c["id"], "title": c["title"], "score": round(c["rerank"], 2)}
                                    for c in find(q, kind, zone, k)]}


@app.post("/ask")
def ask(body: Question):
    return answer(body.question, find(body.question), client())
