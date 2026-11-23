"""Chapter 21: run with  python main.py"""
import asyncio

from client import ask_over_mcp

names, answer = asyncio.run(ask_over_mcp("What is the grapes rate, and what does storing 15 crates for 4 days cost?"))
print("tools from the server:", names)
print(answer)
