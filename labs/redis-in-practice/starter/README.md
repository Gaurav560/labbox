# Brew Point: Redis

Redis runs next to you as `redis`. In the terminal, `redis-cli` is already pointed at it.

- Chapter 1 happens in `redis-cli`.
- Chapter 2 is `app.py`, the menu service. Start it with
  `uvicorn app:app --host 0.0.0.0 --port 8000 --reload`
  and try it from a second terminal with `curl localhost:8000/price/samosa`.
