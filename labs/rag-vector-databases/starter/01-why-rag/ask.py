"""Chapter 1: run with  python ask.py  or  python ask.py "your question"
Asks the model twice: once with only the question, once with the manual sections that keyword search found."""
import sys

from openai import OpenAI

from fieldbook import build_prompt, keyword_search, load_sections

question = sys.argv[1] if len(sys.argv) > 1 else "How often should we change the batteries in the camera traps?"
client = OpenAI()   # LabBox sets OPENAI_BASE_URL and OPENAI_API_KEY: the call goes through the lab's AI gateway

alone = client.chat.completions.create(model="lab-chat", temperature=0,
                                       messages=[{"role": "user", "content": question}])
print("Without the manual:\n" + alone.choices[0].message.content + "\n")

found = keyword_search(question, load_sections())
print("Keyword search found:", [s["id"] for s in found], "\n")
grounded = client.chat.completions.create(model="lab-chat", temperature=0, messages=build_prompt(question, found))
print("With the manual:\n" + grounded.choices[0].message.content)
