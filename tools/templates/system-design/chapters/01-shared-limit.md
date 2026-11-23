:::step{type=story title="One partner, two melting servers"}
:::character{name="Kabir" role="Backend lead, Book Point"}
We opened our quotes API to partners: 10 requests a second each. I wrote the limiter myself and it
passed every test on my laptop. In production we run two servers behind a load balancer, and one
partner's script is getting twice its limit and slowing everyone down. Can you see why?
:::

:::mission
Make the limit hold across both servers: 10 requests a second per API key, proven with a load test.
:::
:::

:::step{type=concept title="Rate limits and where the count lives"}
A **rate limiter** counts each client's requests and answers **429 Too Many Requests** once the
client goes over its limit.

The simplest kind is a **fixed window**: one counter per client per second. The first 10 requests in
a second go through; the rest wait for the next second.

The catch is *where* the counter lives. A dict in your app is per **process**. Behind a load
balancer there are several processes, each with its own dict, so each one allows the full limit.
State that every server must agree on has to live in **one shared place**, like Redis.
:::

:::step{type=predict title="Guess first"}
:::question
The limit is 10 a second, counted in a dict inside the app. Two copies of the app run behind a load
balancer that splits requests evenly. A client sends 30 requests a second. About how many get through?
:::
- [ ] 10 a second
- [x] 20 a second
- [ ] 30 a second
:::explain
Each copy sees about 15 of the 30 and allows 10 of them, so about 20 a second get through: the limit
is multiplied by the number of servers. That is exactly what is happening to Book Point.
:::
:::

:::step{type=try title="See both servers"}
Start the two copies, then ask the load balancer a few times and watch `served_by`:

```bash run
bash run.sh
```

```bash run
for i in 1 2 3 4 5 6; do curl -s -H "X-API-Key: test" http://lb:8080/quote; echo; done
```

Then blast 30 requests in one go and count the answers:

```bash run
for i in $(seq 30); do curl -s -o /dev/null -w "%{http_code}\n" -H "X-API-Key: blast" http://lb:8080/quote; done | sort | uniq -c
```
:::

:::step{type=task task=per_key_limit title="Share the count"}
Change `allow()` in `app.py` so the per-key limit holds **across both copies**: at most
`PER_KEY_LIMIT` requests per second for each API key, counted in Redis. Then run `bash run.sh` again.

The check sends a real load test through the load balancer: one key at 30 a second (about 10 should
get through), another at 4 a second (all should get through), and p95 latency must stay under 50 ms.
:::

:::step{type=recap}
- A rate limiter counts per client and answers 429 over the limit.
- In-memory state is per process: behind a load balancer each server counts alone.
- Shared limits need a shared store; Redis `INCR` with a short `EXPIRE` is a one-line counter.
:::
