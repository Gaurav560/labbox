"""Fieldbook, the rangers' assistant of the Vanrai Hills Wildlife Sanctuary: everything built up to chapter 1.
Each chapter adds its part at the bottom; the parts above it are finished."""
from pathlib import Path
import re

# ---------------------------------------------------------------- chapter 1: words and prompts

STOPWORDS = set("""a an and are as at be by can do does for from has have how i if in is it its me my of on or our
should so that the their them then there they this to was we what when where which who why will with you your""".split())


def load_sections(path="data/manual.md"):
    """The manual's sections: [{"id": "FM-4.2", "title": "Meeting a tiger", "text": "..."}, ...].
    (You will write this yourself in chapter 4, as section_chunks.)"""
    sections = []
    for block in Path(path).read_text().split("\n## ")[1:]:
        heading, _, body = block.partition("\n")
        number, _, title = heading.partition(" ")
        sections.append({"id": number, "title": title, "text": " ".join(body.split())})
    return sections


def words(text):
    """The words of a text that carry meaning, in lower case: "Meeting a tiger!" gives {"meeting", "tiger"}."""
    return {w for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if len(w) > 2 and w not in STOPWORDS}


def keyword_search(question, sections, k=3):
    """The k sections that share the most words with the question, best first. Sections with no shared word are
    left out; equal scores keep the manual's order."""
    asked = words(question)
    scored = []
    for position, section in enumerate(sections):
        shared = len(asked & words(section["title"] + " " + section["text"]))
        if shared > 0:
            scored.append((shared, position, section))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [section for _, _, section in scored[:k]]


SYSTEM = ("You are Fieldbook, the assistant for rangers of the Vanrai Hills Wildlife Sanctuary. Answer only from the "
          "manual sections you are given, in at most three sentences, and name the section you used, like [FM-4.2]. "
          "If the sections do not answer the question, say that the manual does not cover it.")


def build_prompt(question, sections):
    """The messages for the model: SYSTEM, then one user message with the sections and the question."""
    context = "\n\n".join(f"[{s['id']}] {s['title']}\n{s['text']}" for s in sections)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Manual sections:\n\n{context}\n\nQuestion: {question}"},
    ]
