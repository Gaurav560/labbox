"""Answering from the policy wording, with citations: find the clauses a question is about, give only those to the model,
and check that its answer cites them. Run it with: python lookup.py"""
import os
import re

from openai import OpenAI

MODEL = "ai-chat"  # the gateway's name for the model (gpt-4o-mini here); the gateway holds the real key
STOP = {"the", "and", "for", "are", "was", "with", "that", "this", "from", "have", "what", "when", "does", "will", "your",
        "about", "into", "only", "than", "then", "they", "were", "which", "after", "under", "there", "their", "would"}
SYSTEM = (
    "You answer questions from Deccan Shield's adjusters using only the policy clauses given. Cite every clause you use "
    "as [C<number>], for example [C3]. If the clauses do not answer the question, say exactly: Not in the policy wording."
)


def client():
    return OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"], timeout=60, max_retries=2)


def load_clauses(path="data/policy_wording.md"):
    """clause id -> (title, text), from the "C1 | title | text" lines."""
    clauses = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("C") and " | " in line:
                cid, title, text = (part.strip() for part in line.split(" | ", 2))
                clauses[cid] = (title, text)
    return clauses


def words(text):
    """The meaningful words of a text: lower case, 4 letters or more, not in STOP."""
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 4 and w not in STOP}


def find_clauses(question, clauses, k=3):
    """The ids of the k clauses sharing the most meaningful words with the question (title and text), best first;
    ties keep the clause order (C1 before C2). Clauses sharing no word are left out."""
    # TODO (task find_clauses): score each clause by len(words(question) & words(title + " " + text)). Keep the ones
    # with a score above 0, sort by score, highest first (sorted is stable, so ties keep their order), return k ids.
    return []


def cited_answer(question, clauses, openai=None):
    """{"answer": text, "cited": ids the answer cites, "ok": True only if it cites at least one clause and only
    clauses it was given}."""
    ids = find_clauses(question, clauses)
    # TODO (task cited_answer): the user message is the question, then one line per found clause:
    # "[C4] Glass: Breakage of windscreen ...". Ask the model (MODEL, temperature 0, SYSTEM as the system message).
    # cited = the ids in the answer, from re.findall(r"\[(C\d+)\]", answer), in order, without repeats.
    # ok = cited is not empty and every cited id is in ids.
    return {"answer": "", "cited": [], "ok": False}


if __name__ == "__main__":
    clauses = load_clauses()
    for q in ["Is a cracked windscreen paid without the deductible?",
              "My scooter was stolen. What must I send?",
              "Do we pay for a puncture?",
              "Does the policy cover a medical check-up for the driver?"]:
        print("Q:", q)
        print("   clauses:", find_clauses(q, clauses))
        result = cited_answer(q, clauses)
        print("   answer:", result["answer"])
        print("   cited:", result["cited"], "ok:", result["ok"])
