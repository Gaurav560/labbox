"""Chapter 4: run with  python compare_chunks.py   Which way of cutting the manual finds the right section?"""
from pathlib import Path

from fieldbook import embed, load_questions, normalize, section_chunks, top_k, word_chunks

sections = section_chunks(Path("data/manual.md").read_text())
questions = [q for q in load_questions() if all(a.startswith("FM-") for a in q["answers"])]
asked = normalize(embed([q["question"] for q in questions]))


def measure(chunks):
    """Hit rate at 1 and at 3 (is the right section in the best chunk, in the best 3?) and the words the model
    would have to read for the best 3 chunks."""
    vectors = normalize(embed([c["text"] for c in chunks]))
    at1 = at3 = words = 0
    for q, vector in zip(questions, asked):
        best = [chunks[row] for row, _ in top_k(vector, vectors, k=3)]
        at1 += bool(best[0]["ids"] & set(q["answers"]))
        at3 += any(c["ids"] & set(q["answers"]) for c in best)
        words += sum(len(c["text"].split()) for c in best)
    n = len(questions)
    return at1 / n, at3 / n, words / n


def windows(size, overlap):
    """Word windows over the whole manual, ignoring its sections. Each window knows every section it covers."""
    flat, owner = [], []
    for s in sections:
        flat += s["text"].split()
        owner += [s["id"]] * len(s["text"].split())
    return [{"ids": set(owner[i:i + size]), "text": " ".join(flat[i:i + size])} for i in range(0, len(flat), size - overlap)]


print(f"{len(questions)} questions, {len(sections)} sections, {sum(len(s['text'].split()) for s in sections)} words\n")
print(f"{'hit@1':>6} {'hit@3':>6} {'words read':>10} {'chunks':>7}  way of cutting")
for name, chunks in [
    ("windows of 15 words", windows(15, 0)),
    ("windows of 60 words, 10 overlapping", windows(60, 10)),
    ("windows of 300 words, 50 overlapping", windows(300, 50)),
    ("windows of 40 words inside each section", [{"ids": {s["id"]}, "text": piece} for s in sections for piece in word_chunks(s["text"], 40, 10)]),
    ("one chunk per section", [{"ids": {s["id"]}, "text": s["text"]} for s in sections]),
    ("one chunk per section, title first", [{"ids": {s["id"]}, "text": s["title"] + ". " + s["text"]} for s in sections]),
]:
    at1, at3, words = measure(chunks)
    print(f"{at1:6.0%} {at3:6.0%} {words:10.0f} {len(chunks):7}  {name}")
