# Brew Point: Redis

Redis runs next to you as `redis`, and `redis-cli` is already pointed at it.

- Chapters 1 to 4 happen in `redis-cli` (type `redis-cli` on its own for an interactive prompt).
- Chapter 5 is `app.py`, the menu service. Start it with
  `uvicorn app:app --host 0.0.0.0 --port 8000 --reload`
  and try it from a second terminal with `curl localhost:8000/price/samosa`.
