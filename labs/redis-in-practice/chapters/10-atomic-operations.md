:::step{type=story title="Can 500 coins buy 2,000 coins' worth?"}
Basket gives loyalty **coins**: 100 coins off your next order. Asha has 500 coins, so she can redeem five times.

One evening the payments team sees something impossible: a customer with 500 coins redeemed **twenty** times,
and the balance is **minus 1,500**. Nobody broke in. A script on the customer's phone simply sent twenty
redemptions at the same instant, and every one of them was told yes.

The same evening, someone hammers the "send login code" button: Basket sends thousands of text messages to one
phone number, and pays for every one.

Both problems have the same root, and you already met it in chapter 2: **check, then act**, with a gap in between
that other requests can slip through. This chapter closes that gap, in your app, for real.

:::mission
Allow at most three login codes a minute per phone, and make it impossible to spend the same coins twice.
:::
:::

:::step{type=concept title="Check, then act: the gap"}
Look at `redeem()` in `10-atomic-operations/app.py`, lines 23 to 34. It reads like perfectly sensible code:

1. **Read** the balance (line 27).
2. **Check** it is enough (line 30).
3. Do some work: confirm the order with the payments service (line 32, 100 ms).
4. **Spend**: take the coins off (line 33).

Run one request at a time and it is perfect. Run twenty at once, and all twenty do step 1 before any of them
reaches step 4. All twenty read 500, all twenty pass the check, all twenty spend. This pattern is called
**check-then-act**, and it is the most common concurrency bug in web apps: booking systems, wallets, coupons,
stock counts, "only one free trial per customer".

:::trace{title='twenty redemptions of 100 coins, check-then-act'}
| moment | request 1 | request 2 | ... requests 3 to 20 | coins:42 | note |
|---|---|---|---|---|---|
| start |  |  |  | 500 | Twenty redemptions arrive together. |
| read | GET: 500 | GET: 500 | GET: 500 each | 500 | Everyone reads before anyone spends. |
| check | 500 >= 100: ok | 500 >= 100: ok | ok each | 500 | Every check passes, because every check saw 500. |
| work | payments, 100 ms | payments, 100 ms | the same | 500 | The gap: a tenth of a second, for every request at once. |
| spend | DECRBY: 400 | DECRBY: 300 | down to -1500 | -1500 | Twenty spends. The balance goes far below zero. |
:::

The cure is to make the check and the change **one single step** that nothing can come between. Redis gives you
two ways: commands that already check and change in one go (like `INCR`, which returns the new count), and
**scripts**, which you will meet below.
:::

:::step{type=try title="Make it race" file="10-atomic-operations/race.py" line="13-26"}
Let's see it on your own app. Stop the previous app and start this chapter's:

```bash run
cd /workspace/10-atomic-operations && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

First, one redemption at a time. Give customer 7 three hundred coins and redeem four times:

```bash run
redis-cli SET coins:7 300
```

```bash run
for i in 1 2 3 4; do curl -s -X POST "localhost:8000/redeem/7?coins=100"; echo; done
```

```text
{"redeemed":100,"left":200}
{"redeemed":100,"left":100}
{"redeemed":100,"left":0}
{"detail":"Not enough coins"}
```

Correct. Now `race.py` gives Asha (customer 42) 500 coins and sends twenty redemptions **at once**:

```bash run
python3 race.py
```

```text
200: 20, 409: 0, coins left: -1500
```

All twenty went through. Asha got 2,000 coins' worth of discounts from 500 coins. Run it a few times: it fails the
same way every time, because the 100 ms payments check leaves a wide gap.

And the login codes: four in a row, all sent.

```bash run
for i in 1 2 3 4; do curl -s -X POST -o /dev/null -w "%{http_code} " localhost:8000/otp/9000000001; done
```

```text
200 200 200 200
```
:::

:::step{type=example title="Worked example: at most 5 wrong passwords a minute"}
The login-code limit is a **rate limit**: at most N actions per time window. Here is the classic Redis way to do
it, on a different problem: lock an account after 5 wrong passwords in a minute.

```text
> INCR login:fails:asha
(integer) 1
> EXPIRE login:fails:asha 60
(integer) 1
> INCR login:fails:asha
(integer) 2
> INCR login:fails:asha
(integer) 3
> TTL login:fails:asha
(integer) 60
```

In code, every wrong password does this:

```python
fails = r.incr(f"login:fails:{user}")
if fails == 1:
    r.expire(f"login:fails:{user}", 60)
if fails > 5:
    raise HTTPException(status_code=429, detail="Too many attempts")
```

1. `INCR` adds one **and returns the new count**, in one step. There is no separate read, so there is no gap:
   twenty wrong passwords at once get the counts 1 to 20, never twenty 1s.
2. Only the **first** attempt of the window (`fails == 1`) starts the 60 second clock. Setting it every time
   would push the window forward forever, and a patient attacker would never be unlocked; nor would Asha.
3. Once the count passes the limit, answer **429 Too Many Requests**, the HTTP status made for this.
4. When the key expires, the count starts again from nothing.

This is called a **fixed window** limit: one counter per minute window. It is simple and good enough for most
limits; the deep dive mentions smarter ones.

A metro turnstile is a rate limit you can touch: it counts people through, one at a time, and stops the next one when the rules say so.

:::photo{src="/lesson-images/redis/turnstile.webp" alt="A stainless steel metro turnstile with a round blue card reader and an arrow sign, in a Stockholm station" credit="Leo Johannes" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Turnstile_in_Stockholm_Metro_station_in_Slussen-1.jpg"}
A turnstile in the Stockholm metro.
:::
:::

:::step{type=predict title="Guess first"}
:::question
In the rate limit, what goes wrong if you call `EXPIRE key 60` after **every** `INCR`, not just the first?
:::
- [ ] Nothing, it just resets the same timer
- [x] The window never ends while attempts keep coming: each one pushes the expiry 60 seconds further
- [ ] The count goes back to zero every time
:::explain
Each `EXPIRE` restarts the clock. Someone trying once every 50 seconds would keep the counter alive forever, and
a real user who made five mistakes could stay locked out for as long as anyone keeps trying.
:::
:::

:::step{type=task task=otp_limit title="Your turn: stop the login code spam"}
In `send_otp()` in `app.py`, allow at most **3** login codes per phone number per minute:

1. Count the codes in Redis under `otp:count:<phone>`, with `INCR`.
2. The first code of a window starts a 60 second lifetime on that key.
3. When the count goes over 3, raise `HTTPException(status_code=429, ...)` instead of sending.

Four calls in a row (the loop above) should now print `200 200 200 429`. Press **Check**.
:::

:::step{type=concept title="Scripts: your own atomic command"}
The coins need more than `INCR`. "Spend 100 coins, but **only if** there are at least 100" is a check **and**
a change, and no single built-in command does exactly that. (`DECRBY` alone would happily go below zero.)

So Redis lets you write your own command, as a small **script** in the Lua language, and run it **inside**
Redis with `EVAL`. Redis runs a script like any other command: from start to finish, with nothing else running in
between. Whatever the script reads cannot change before it writes.

Here is the spending rule as a script, tried in `redis-cli` on a balance of 250:

```text
> SET coins:9 250
OK
> EVAL "local b = tonumber(redis.call('GET', KEYS[1]) or '0') if b < tonumber(ARGV[1]) then return -1 end return redis.call('DECRBY', KEYS[1], ARGV[1])" 1 coins:9 100
(integer) 150
```

Run the same `EVAL` again and it answers `(integer) 50`; a third time, `(integer) -1`, and `GET coins:9` still
says `"50"`. The script refused, and the balance never went below zero.

Read the script piece by piece. Laid out on several lines it is:

```lua
local b = tonumber(redis.call('GET', KEYS[1]) or '0')
if b < tonumber(ARGV[1]) then return -1 end
return redis.call('DECRBY', KEYS[1], ARGV[1])
```

1. `redis.call('GET', KEYS[1])` runs a normal Redis command from inside the script. `KEYS[1]` is the first key
   name passed in (`coins:9`); `or '0'` treats a missing key as zero; `tonumber` makes it a number.
2. `ARGV[1]` is the first extra argument, the cost (`100`). If the balance is too small, the script returns `-1`,
   our signal for "not enough", and changes nothing.
3. Otherwise it spends with `DECRBY` and returns the new balance.

In the `EVAL` line, the `1` after the script says how many of the following words are **key names** (one:
`coins:9`); the rest (`100`) are arguments. Keys are passed separately so that Redis Cluster (chapter 16) knows
which server must run the script.

From Python, `r.register_script(...)` turns a script into a function you call with `keys=[...]` and `args=[...]`.
It loads the script into Redis once and then runs it by its fingerprint, so the script text is not sent every
time.
:::

:::step{type=task task=redeem_points title="Your turn: no more free coins"}
Make `redeem()` in `app.py` safe against twenty requests at once:

1. At the top of the file, after `r` is made, register a Lua script that reads the balance, returns `-1` when it is
   less than the cost, and otherwise spends it with `DECRBY` and returns what is left (the one above works).
2. In `redeem()`, replace the read, check and `decrby` with one call of that script (`keys=[key]`,
   `args=[coins]`).
3. If it returns a negative number, raise a 409; otherwise return `{"redeemed": coins, "left": ...}`.

You may keep or drop the payments check: once the spend is one step, the gap no longer matters. Run
`python3 race.py`: it should say `200: 5, 409: 15, coins left: 0`, every time. Press **Check**.
:::

:::step{type=try title="Both fixed"}
With both tasks done, this lab's app answered:

```text
200 200 200 429
```

and the fifth attempt said why:

```text
{"detail":"Too many login codes. Try again in a minute."}
```

`GET otp:count:9000000001` showed `"5"` and `TTL` showed 60: the window started with the first code and will end
on its own. The race, three runs in a row:

```text
200: 5, 409: 15, coins left: 0
200: 5, 409: 15, coins left: 0
200: 5, 409: 15, coins left: 0
```

Exactly five through, every time, however the requests interleave.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is `INCR` followed by a check of the number it returns safe, while `GET`, check, `SET` is not?
:::
- [ ] `INCR` is faster than `GET`
- [x] `INCR` changes the value and gives back the result in one step, so each request gets its own, different count
- [ ] `INCR` locks the key
:::explain
With `INCR`, twenty requests get 1, 2, 3 and so on up to 20, and each decides on its own number. With `GET` they
can all read the same number before any of them writes.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
A Lua script running inside Redis takes 200 ms because it loops over a huge list. What happens meanwhile?
:::
- [ ] Other clients are served in parallel
- [x] Every other client waits: a script runs as one command, and Redis runs one command at a time
- [ ] Redis stops the script after 100 ms
:::explain
The same property that makes a script atomic makes a slow script freeze everyone. Keep scripts small: a few reads
and writes on a few keys.
:::
:::

:::step{type=deep-dive title="Go deeper: transactions, WATCH, and smarter rate limits"}
**MULTI and EXEC.** A transaction queues commands and runs them as one block. But inside it you cannot read a
value and decide on it, because nothing runs until `EXEC`. So for check-then-act, transactions add **WATCH**: you
`WATCH coins:42`, read it, then `MULTI ... EXEC`. If anyone changed the key between your `WATCH` and your `EXEC`,
the transaction is cancelled and you try again. That is **optimistic locking**. It works, but under heavy
contention many requests retry, which is why a script is usually simpler and faster.

**Functions.** Since Redis 7 you can also load scripts permanently as **functions** (`FUNCTION LOAD`), named and
versioned, instead of sending them with each deploy.

**Better rate limits.** A fixed window allows a burst at the edge: 3 codes at 10:00:59 and 3 more at 10:01:00.
A **sliding window** counts the last 60 seconds exactly, for example with a sorted set of timestamps
(`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`, all in one script). A **token bucket** allows short bursts but a steady
average. LabBox has a whole lab on rate limiters if you want to go further.

**Rate limits protect money, too.** Every login code costs Basket a text message. Rate limits on anything that
costs money per call (texts, emails, paid APIs) are as important as the ones that stop attackers.
:::

:::step{type=recap}
You can now:

- recognise check-then-act races, and reproduce one with many requests at once;
- build a fixed-window rate limit with `INCR` and an `EXPIRE` on the first hit, answering 429;
- write a small Lua script and run it with `EVAL`, or from Python with `register_script`;
- explain why a script is atomic, and why it must stay small.

Next, chapter 11: locks, for work that must happen once and only once.

:::photo{src="/lesson-images/redis/redis-10-notes.webp" alt="Handwritten notes about atomic operations: check, then act = a race; INCR + EXPIRE = a rate limit; 429 = too many requests; a Lua script runs alone; keep scripts small" ai="true"}
One page of notes for this chapter.
:::
:::
