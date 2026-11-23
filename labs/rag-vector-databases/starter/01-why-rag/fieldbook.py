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
    # TODO (task keyword_search): score every section by how many of the question's words (use words()) appear in
    #   its title and text. Leave out sections that score 0, sort the rest best first (equal scores keep the
    #   manual's order), and return the first k sections.
    raise NotImplementedError("task keyword_search")


SYSTEM = ("You are Fieldbook, the assistant for rangers of the Vanrai Hills Wildlife Sanctuary. Answer only from the "
          "manual sections you are given, in at most three sentences, and name the section you used, like [FM-4.2]. "
          "If the sections do not answer the question, say that the manual does not cover it.")


def build_prompt(question, sections):
    """The messages for the model: SYSTEM, then one user message with the sections and the question."""
    # TODO (task context_prompt): return two messages. The first is the system message, SYSTEM. The second is a user
    #   message that starts with "Manual sections:", then every section as "[FM-4.2] Meeting a tiger" on one line
    #   and its text on the next (sections separated by a blank line), and ends with "Question: " and the question.
    raise NotImplementedError("task context_prompt")
