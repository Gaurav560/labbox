"""Chapter 11: run with  python ask.py  or  python ask.py "your question"
Two-stage retrieval, then an answer that cites its sources, or an honest "not found"."""
import sys

from openai import OpenAI

from fieldbook import Index, answer, load_corpus, two_stage

index = Index(load_corpus())
client = OpenAI()
questions = sys.argv[1:] or ["What should the crew do when the treetops are burning?",
                             "Which animal injures the most people?",
                             "How many tigers live in Vanrai?",
                             "What is the entry fee for a foreign tourist?"]
for question in questions:
    sources = two_stage(question, index)
    result = answer(question, sources, client)
    print(question)
    print("  best source:", f"{sources[0]['id']} ({sources[0]['rerank']:.1f})")
    print("  " + result["answer"])
    print("  sources:", result["sources"], "\n")
