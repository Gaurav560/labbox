:::step{type=story title="Free coffee for everyone"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Two things went wrong last week. A bot pressed "send OTP" four thousand times on one phone number,
and we paid for every SMS. And a customer with 500 loyalty points tapped "redeem" on two phones at
once, again and again, and walked out with nine free coffees. Both bugs have the same root: our code
checks something, then acts on it, and the world changes in between.
:::

:::mission
Limit OTPs per phone, and make loyalty redemptions impossible to double-spend.
:::
:::

:::step{type=concept title="Check, then act: the race"}
The redeem endpoint does three things: **read** the balance, **check** it covers the cost, **write**
the new balance. Run it twice at the same moment:

```text
request A: read 500        request B: read 500
request A: 500 >= 100 ok   request B: 500 >= 100 ok
request A: write 400       request B: write 400
```

Two coffees, one deduction. Each line is correct; the problem is what runs **between** them.

Single commands like `INCR` are safe because Redis runs each one alone. When the check and the
write are separate commands, you need them to run as **one** step.
:::

:::step{type=example title="Worked example: at most 5 login tries a minute"}
A counter that resets itself is a rate limiter in two commands. Here, login tries per IP address:

```python
def allow_login(ip):
    key = f"login:tries:{ip}"
    tries = r.incr(key)          # 1. count this try, atomically
    if tries == 1:
        r.expire(key, 60)        # 2. the first try starts the 60 second window
    return tries <= 5            # 3. the 6th try in the window is refused
```

1. `INCR` creates the key at 1 and adds one each time, with no race.
2. Only the first try sets the timer, so the window is fixed, not sliding.
3. After 60 seconds the key expires and the count starts again from zero.
:::

:::step{type=predict title="Guess first"}
:::question
A balance of 500 points, and 20 requests to redeem 100 arrive at the same moment. With the read, check, write code, how many succeed?
:::
- [ ] Exactly 5
- [x] Often more than 5, and the balance can end above zero
- [ ] None: they block each other
:::explain
Many requests read the same balance before any of them writes, so several approve against money
that was already spent. The final balance is simply whichever write landed last.
:::
:::

:::step{type=try title="Make it race"}
Give customer 77 some points, then fire 20 redemptions at once:

```bash run
redis-cli SET loyalty:77 500
```

```bash run
for i in $(seq 20); do curl -s -o /dev/null -w "%{http_code} " -X POST "localhost:8000/redeem/77?points=100" & done; wait; echo; redis-cli GET loyalty:77
```

Count the 200s. More than five is free coffee.
:::

:::step{type=task task=otp_limit title="Stop the OTP spam"}
Make `POST /otp/{phone}` allow at most **3 calls per phone number per minute**. The 4th call within the
minute must get status **429** (Too Many Requests).

Keep the count in Redis under `otp:count:<phone>`, and let it reset after 60 seconds.
:::

:::step{type=concept title="Scripts: your own atomic command"}
Redis can run a small **Lua** script as one command. Nothing else runs until it finishes, so the
read, the check and the write inside it can never be split:

```lua
local balance = tonumber(redis.call('GET', KEYS[1]) or '0')
if balance < tonumber(ARGV[1]) then return -1 end
return redis.call('DECRBY', KEYS[1], ARGV[1])
```

In Python, `r.register_script(source)` gives you a callable: `spend(keys=[...], args=[...])`.

The other tool is **`WATCH`**: a transaction that is cancelled if a watched key changed since you
read it, so you retry. Scripts are usually simpler.

:::trace{title="300 points, four redemptions of 100 at once, through the script"}
| request | balance before | script answers | balance after | note |
|---|---|---|---|---|
| 1 | 300 | 200 | 200 | The script reads, checks and spends as one command. |
| 2 | 200 | 100 | 100 | The next request runs only after the first has finished. |
| 3 | 100 | 0 | 0 | Still enough: spent. |
| 4 | 0 | -1 | 0 | Not enough left: the script answers -1 and spends nothing. That is a 409. |
:::
:::

:::step{type=task task=redeem_points title="No more free coffee"}
Make `POST /redeem/{cid}` spend points **atomically**: with 500 points, 20 redemptions of 100 at the
same moment must give exactly **5** successes, **15** answers of **409**, and a balance of **0**,
never below.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is `INCR` plus `EXPIRE` safe for a rate limit, while read, check, write is not?
:::
- [ ] `INCR` is faster
- [x] `INCR` counts and returns the new value in one atomic step, so two requests can never both see the same count
- [ ] `EXPIRE` locks the key
:::explain
Each `INCR` answers a different number, so the fourth request sees 4 and is refused. With read, check, write, two requests can both read 2 and both pass.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A Lua script runs for 2 seconds. What do other clients experience?
:::
- [ ] Nothing: scripts run in the background
- [x] They all wait: Redis runs nothing else until the script finishes
- [ ] Their commands fail with an error
:::explain
A script is one atomic command on the single main thread. That is what makes it safe, and why scripts must stay short.
:::
:::

:::step{type=deep-dive title="Scripts in production"}
**Keep scripts short.** While a script runs, Redis serves no one else. A loop over a million keys
inside Lua freezes every client.

**Pass every key in `KEYS`.** It is not just style: Redis Cluster uses the key names to know which
node must run the script, so all of a script's keys must live on the same node.

**`EVALSHA`.** The client sends the script once and then only its SHA1 hash; `register_script` does
this for you, and reloads the script if Redis restarted and forgot it.

**Functions.** Redis 7 adds `FUNCTION LOAD`: named, persistent scripts that survive restarts, for logic
you share across services.
:::

:::step{type=recap}
- Check, then act is a race whenever the check and the action are separate steps.
- `INCR` plus `EXPIRE` is a per-caller counter that resets itself: a simple rate limiter.
- A Lua script runs as one atomic command: read, check and write with nothing in between.
- `WATCH` is the optimistic alternative: abort and retry if the key changed.
:::
