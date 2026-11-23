"""Chapter 2: run with  python main.py"""
from tokens import count_tokens, fit_window, pieces

for text in ["What is the onion rate today?", "aaj kandyacha bhav kay aahe?", "आज कांद्याचा भाव काय आहे?"]:
    print(f"{count_tokens(text):3} tokens  {pieces(text)}")

chat = ["Hello, I am Ravi from Lasalgaon.", "I grow onions on 3 acres.", "My cold storage booking is 40 crates.",
        "Can I add 20 more crates next week?"]
print("\nfits in 25 tokens:", fit_window(chat, 25))
