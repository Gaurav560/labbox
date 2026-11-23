"""Chapter 1: run with  python main.py"""
from learn import EXAMPLES, accuracy, learn_threshold
from rules import rule_reply

for message in ["When is the office open?", "What is the onion rate today?", "When can I come in?", "kanda bhav?"]:
    print(f"{message!r:34} -> {rule_reply(message)}")

threshold = learn_threshold(EXAMPLES)
print(f"\nlearned: skip irrigation when rain >= {threshold} mm ({accuracy(threshold, EXAMPLES):.0%} of the examples right)")
