"""Chapter 4: run with  python main.py"""
from attention import attention, softmax

words = ["rate", "price", "spray", "harvest"]
scores = [2.0, 1.6, 0.4, 0.1]  # how much a model "likes" each next word after "What is today's onion ..."
for t in (0.2, 1.0, 2.0):
    print(f"temperature {t}: " + ", ".join(f"{w} {p:.2f}" for w, p in zip(words, softmax(scores, t))))

# Which earlier word should "it" look at in "The farmer sprayed the vines because it rained"?
keys = {"farmer": [0.9, 0.1, 0.0], "vines": [0.2, 0.8, 0.1], "rained": [0.1, 0.3, 0.9]}
query_it = [0.1, 0.9, 0.3]
weights = attention(query_it, list(keys.values()))
print("\nattention of 'it':", ", ".join(f"{w} {p:.2f}" for w, p in zip(keys, weights)))
