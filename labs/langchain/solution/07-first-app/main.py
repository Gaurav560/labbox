"""Chapter 7: run with  python main.py"""
from app import ask, chat_model

model = chat_model()
print(type(model).__name__)
print(ask(model, "I am a new member. What can you help me with?"))
