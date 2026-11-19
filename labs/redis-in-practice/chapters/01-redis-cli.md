:::step{type=story title="Too slow, too busy"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Every app call goes to Postgres or to our old billing system, and lunch time is getting slow.
Before we put Redis in front of anything, I want you to know it from the inside: its keys,
its types, and how keys can expire on their own.
:::

:::mission
Store the menu, a one-time password and today's best sellers in Redis, from the terminal.
:::
:::

:::step{type=concept title="Keys, values, types"}
Redis is a database that keeps everything **in memory**, so reads and writes take well under a
millisecond. Every piece of data lives under a **key**, and each key holds one **type**:

| Type | Holds | Commands |
|---|---|---|
| string | one value | `SET`, `GET`, `INCR` |
| hash | fields and values, like a small dict | `HSET`, `HGET`, `HGETALL` |
| sorted set | members ordered by a score | `ZADD`, `ZINCRBY`, `ZRANGE` |

Any key can be given a **TTL** (time to live): after that many seconds Redis deletes it.

:::tip
Names with a colon, like `otp:9876543210`, are only a habit. Redis sees one plain key; the colon
helps people read it.
:::
:::

:::step{type=predict title="Guess first"}
:::question
You run `SET greeting hello EX 10`, wait 15 seconds, then `GET greeting`. What comes back?
:::
- [ ] `"hello"`
- [x] `(nil)`, the key is gone
- [ ] An error: the key expired
:::explain
`EX 10` gives the key 10 seconds to live. After that Redis deletes it, and `GET` on a missing key
returns nil. Nothing errors: the key simply does not exist anymore.
:::
:::

:::step{type=try title="Say hello to Redis"}
`redis-cli` is already connected to the lab's Redis. Try a few commands:

```bash run
redis-cli SET greeting hello EX 10
```

```bash run
redis-cli TTL greeting
```

Run `TTL` again after a few seconds: it counts down, and gives `-2` once the key is gone.
:::

:::step{type=task task=menu_hash title="A hash for the menu"}
Store the menu as a **hash** under the key `menu`, with one field per item:

| field | value |
|---|---|
| `filter coffee` | `30` |
| `cold coffee` | `40` |
| `vada pav` | `25` |

Run `redis-cli` with no arguments to type several commands in a row (`exit` leaves).
:::

:::step{type=task task=otp_expiry title="An OTP that expires"}
A customer asked for a login code. Store the OTP `4821` under `otp:9876543210` so that it
**disappears by itself after 5 minutes**.

:::warning
If you take longer than 5 minutes before pressing Check, the key will be gone. That is the point:
just set it again.
:::
:::

:::step{type=task task=top_sellers title="Today's best sellers"}
Keep today's sales in a **sorted set** called `sales:today`: filter coffee sold `120`,
vada pav `80`, cold coffee `45`.

Then the evening rush sells **5 more** cold coffees. Add them to its score without retyping
the others.
:::

:::step{type=recap}
- Redis keeps data in memory under keys; each key has one type.
- Hashes are small dicts, sorted sets keep members ordered by a score.
- `EX` or `EXPIRE` gives a key a TTL; `TTL` shows what is left (`-1` never expires, `-2` gone).
:::
