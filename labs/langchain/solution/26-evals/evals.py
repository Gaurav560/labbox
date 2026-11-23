"""Testing Navin: a golden set of questions, and a second model that grades each answer against the rule."""
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

GOLDEN = [
    ("Can I store 80 crates of onions? How long until I know?", "approval", "storage.txt"),
    ("I sprayed my grapes on Monday. Can I harvest on Friday?", "10 days", "spraying.txt"),
    ("How much loan can I get for 4 acres?", "2,00,000", "loans.txt"),
    ("When will the money from my sale reach me?", "3 working days", "market.txt"),
    ("What does it cost to join the co-op?", "1,000", "membership.txt"),
    ("Do you buy garlic?", "don't know", None),
]


def pass_rate(answers: list[str], golden: list[tuple]) -> float:
    """The share of answers that contain their golden phrase, ignoring capitals."""
    passed = sum(1 for answer, (_, phrase, _) in zip(answers, golden) if phrase.lower() in answer.lower())
    return passed / len(golden)


class Grade(BaseModel):
    """A judge's verdict on one answer."""
    correct: bool = Field(description="true only if the answer agrees with the rule in every detail")
    reason: str = Field(description="one sentence: what is right or wrong")


JUDGE = ("You check a help desk's answer against the co-op's rule. Rule:\n{rule}\n\nQuestion: {question}\n"
         "Answer: {answer}\n\nIs the answer correct according to the rule?")


def judge(question: str, answer: str, rule: str) -> Grade:
    model = init_chat_model("openai:ai-chat", temperature=0)
    return model.with_structured_output(Grade).invoke(JUDGE.format(rule=rule, question=question, answer=answer))
