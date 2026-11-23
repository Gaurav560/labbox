#!/usr/bin/env bash
# Chapter 27: start the server in one terminal (uvicorn app:app --port 8000), then run this in another.
ask() { curl -s localhost:8000/chat -H 'Content-Type: application/json' -d "{\"member_id\": \"$1\", \"message\": \"$2\"}"; echo; echo; }
ask M-104 "Hello, I am Ravi. I grow onions on 3 acres in Lasalgaon."
ask M-104 "Can I store 80 crates of onions? How long until I know?"
ask M-104 "Please book 80 crates of onions for 10 days."
curl -s localhost:8000/manager/decide -H 'Content-Type: application/json' -d '{"member_id": "M-104", "decision": {"type": "approve"}}'; echo; echo
ask M-104 "My Aadhaar is 4821 3390 1176, please note it."
ask M-104 "How much loan can I get for my farm?"
