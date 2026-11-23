"""Chapter 20: run with  python main.py"""
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_text_splitters import RecursiveCharacterTextSplitter

from loader import load_rules, split
from quality import GOLDEN, hit_rate, titled_chunks
from store import build_store

docs = load_rules(Path("rules"))
titles = {d.metadata["source"]: d.page_content.splitlines()[0] for d in docs}


def sources(store):
    return lambda q: [d.metadata["source"] for d, _ in store.similarity_search_with_score(q, k=3)]


plain = build_store(split(docs))
titled = build_store(titled_chunks(split(docs), titles))
for name, store in [("plain chunks ", plain), ("titled chunks", titled)]:
    print(f"{name}: hit@1 {hit_rate(sources(store), GOLDEN, 1):.0%}, hit@3 {hit_rate(sources(store), GOLDEN, 3):.0%}")
    for q, want in GOLDEN:
        got = sources(store)(q)
        if got[0] != want:
            print(f"    miss@1 {q!r}: {got}")

# Where are the chunk boundaries? The rule files wrap their lines, and the default splitter cuts at line breaks.
sentences = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30, separators=["\n\n", ". ", "\n", " ", ""])
for name, chunks in [("line breaks", split(docs)), ("sentences", sentences.split_documents(docs))]:
    print(f"\nsplit at {name}: the chunks about more than 50 crates:")
    for chunk in chunks:
        if "more than 50" in chunk.page_content or chunk.page_content.startswith("crates need"):
            print(f"    {chunk.page_content!r}")

# Query rewriting: the model turns the member's words into a clear English search query first.
model = init_chat_model("openai:ai-chat", temperature=0)
question = "kanda thevaycha aahe, kiti paise lagtil?"
for prompt in ["Rewrite this farmer's question as a short English search query about a cooperative's rules. "
               "Reply with the query only: ",
               "The farmer writes Marathi in English letters (kanda means onion, thevaycha means to store). Translate the "
               "question into English, as a short search query. Reply with the query only: "]:
    query = model.invoke(prompt + question).content
    print(f"\nrewritten: {question!r} -> {query!r}: {sources(titled)(query)}")
