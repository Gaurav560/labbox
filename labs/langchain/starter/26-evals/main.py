"""Chapter 26: run with  python main.py"""
from pathlib import Path

from evals import GOLDEN, judge, pass_rate
from rag import rag_agent

agent = rag_agent()
answers = []
for question, phrase, rule_file in GOLDEN:
    answer = agent.invoke({"messages": [{"role": "user", "content": question}]})["messages"][-1].content
    answers.append(answer)
    verdict = ""
    if rule_file:
        grade = judge(question, answer, Path("rules", rule_file).read_text())
        verdict = f"judge: {'correct' if grade.correct else 'WRONG'}: {grade.reason}"
    print(f"> {question}\n  {answer}\n  phrase {phrase!r}: {'found' if phrase.lower() in answer.lower() else 'MISSING'}  {verdict}\n")
print(f"golden set: {pass_rate(answers, GOLDEN):.0%} of the answers contain their phrase")
