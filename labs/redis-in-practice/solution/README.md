# Basket: Redis in practice

Basket is a 10-minute grocery delivery app in Pune. Redis runs next to you as `redis` (and a second server as
`replica`); `redis-cli` and `redis-benchmark` are already pointed at it.

- Chapters 1 to 5 and 12 to 16 happen in the terminal: type `redis-cli` on its own for an interactive prompt.
- Chapters 6 to 11 and 17 each have their own folder with an `app.py`. Start a chapter's app from its folder:

      cd /workspace/07-caching && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

  and call it from a second terminal, for example `curl localhost:8000/price/rice`. Only one app can use port
  8000 at a time: stop the previous chapter's app with Ctrl+C first.
- `catalogue.py` is Basket's slow catalogue service (1.5 s and Rs 0.10 per call). You never change it.
