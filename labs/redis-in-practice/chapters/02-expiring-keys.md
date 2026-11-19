:::step{type=story title="Data with a use-by date"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Some data should not live forever. A login code is useless after five minutes. A session should end
when a customer walks away. Today our app deletes these by hand, with a nightly script that someone
forgot to run in October. Redis can do it for us, to the second.
:::

:::mission
Give data a lifetime: a login code that expires on its own, a session with a time limit, and a promo you rescue from expiring.
:::
:::

:::step{type=concept title="A key with a timer"}
Any key can carry a **time to live** (TTL): a number of seconds after which Redis deletes it. You can
set it with the value, or add it later:

```text
> SET otp:98765 4821 EX 300      value and a 5 minute timer, in one step
> EXPIRE session:7f3a 1800       a 30 minute timer on an existing key
> TTL otp:98765
(integer) 297
```

`TTL` counts down. It answers `-1` for a key with no timer, and `-2` for a key that does not exist,
which also covers "it already expired". `PERSIST` removes a timer and keeps the key forever.
:::

:::step{type=predict title="Guess first"}
:::question
You run `SET greeting hello EX 10`, wait 15 seconds, then `GET greeting`. What comes back?
:::
- [ ] `"hello"`: expired keys stay readable until you delete them
- [x] `(nil)`: the key is gone
- [ ] An error saying the key expired
:::explain
After its TTL a key simply stops existing. `GET` on a missing key returns nil, with no error. Code
that reads expiring keys must always be ready for "not there".
:::
:::

:::step{type=try title="Watch a timer run"}
```bash run
redis-cli SET greeting hello EX 10
```

Run this a few times over the next ten seconds and watch it count down, then turn into `-2`:

```bash run
redis-cli TTL greeting
```
:::

:::step{type=task task=otp_expiry title="A login code that expires"}
A customer asked for a login code. Store the code `4821` under `otp:9876543210` so that it
**disappears by itself after 5 minutes**.

:::warning
If you take longer than 5 minutes before pressing Check, the code will be gone. That is the point: set it again.
:::
:::

:::step{type=concept title="Timers on keys that already exist"}
Real systems often add or change a timer after the fact. Two things to know.

**Writing a key again with plain `SET` removes its timer.** `SET session:7f3a newvalue` turns a
30 minute session into a forever session, a classic bug. `SET ... KEEPTTL` keeps the timer.

**`EXPIRE` resets the clock.** Calling `EXPIRE session:7f3a 1800` on every request gives you a
**sliding** session: it ends 30 minutes after the customer's *last* visit, not their first.
:::

:::step{type=task task=session_ttl title="End the endless session"}
A bug left the login session `session:7f3a` with no timer at all, so it would stay logged in forever.
Give it a **30 minute** lifetime without changing its value.
:::

:::step{type=task task=keep_forever title="Rescue the promo"}
`promo:diwali` was created with a one hour timer, but marketing has just extended the offer
indefinitely. Make the key **permanent**, keeping its value.
:::

:::step{type=deep-dive title="How Redis expires keys"}
Redis does not set a million alarms. It deletes expired keys in two ways.

**Lazily:** whenever a command touches a key, Redis first checks its expiry, and deletes it if it is
past due. An expired key is never returned.

**Actively:** about ten times a second, Redis samples a few keys that have a TTL and deletes the
expired ones, repeating while many of the sample were expired.

So memory from expired keys is freed soon, but not at the exact millisecond. And because both
happen on Redis's single thread, millions of keys expiring in the same second can cause a short
latency spike: add a little random jitter to TTLs you set in bulk.
:::

:::step{type=recap}
- `SET key value EX seconds` stores a value with a timer; `EXPIRE` adds one later.
- `TTL` shows the seconds left: `-1` means no timer, `-2` means gone.
- Plain `SET` drops the timer; use `KEEPTTL` to keep it. `PERSIST` makes a key permanent.
- Refreshing `EXPIRE` on every request gives a sliding timeout.
:::
