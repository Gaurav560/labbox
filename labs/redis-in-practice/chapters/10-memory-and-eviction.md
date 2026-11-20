:::step{type=story title="OOM at lunch rush"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
12:40, the busiest minute of the day, and every login is failing. The app logs say the same line a
thousand times: "OOM command not allowed when used memory > 'maxmemory'". Redis is full, and it is
refusing every write. Nobody deployed anything today. Something has been growing quietly for weeks.
:::

:::mission
Find what filled Redis, remove it safely, and set a policy so a full Redis drops cache entries instead of refusing writes.
:::
:::

:::step{type=concept title="Redis lives inside a memory budget"}
Redis keeps everything in RAM, so you give it a budget: `maxmemory` (ours is 64 MB). What happens at
the limit is the **eviction policy**:

| policy | when full |
|---|---|
| `noeviction` | refuse writes with an OOM error (the default) |
| `allkeys-lru` | delete the least recently used key, any key |
| `volatile-lru` | delete the least recently used key **that has a TTL** |

There are LFU (least *frequently* used), random and TTL variants too. The important choice is
`allkeys` versus `volatile`: may Redis throw away **any** key, or only cache entries?

:::trace{title="Redis is full and a new write arrives, with volatile-lru"}
| key | has a TTL? | last used | evicted? | note |
|---|---|---|---|---|
| cart:42 | no | an hour ago | no | No TTL: volatile policies never touch it. |
| price:samosa | yes | 30 minutes ago | yes | The least recently used key with a TTL goes first. |
| price:poha | yes | 2 seconds ago | no | Recently used: kept. |
| session:7f3a | yes | 1 minute ago | no | Enough room was freed by one eviction. |
:::
:::

:::step{type=example title="Worked example: how big is that key?"}
Before deleting anything, measure. Here is a quick look at one suspicious key:

```text
> TYPE events:debug
list
> LLEN events:debug
(integer) 812345
> MEMORY USAGE events:debug
(integer) 52113408
> TTL events:debug
(integer) -1
```

1. `TYPE` says what kind of key it is, so you pick the right size command.
2. `LLEN` counts its elements without reading them: never `LRANGE 0 -1` a big list.
3. `MEMORY USAGE` gives bytes: about 50 MB, most of a 64 MB budget.
4. `TTL -1`: it never expires. A debug log that only grows is a classic culprit.
:::

:::step{type=predict title="Guess first"}
:::question
Redis holds the cache (keys with a TTL) and the shopping carts (no TTL). It is full, with `allkeys-lru`. What can happen to a cart nobody touched for an hour?
:::
- [ ] Nothing: carts are safe because they have no TTL
- [x] It can be evicted, and the customer's cart is simply gone
- [ ] Redis refuses to evict it and returns an error
:::explain
`allkeys` policies may evict any key, carts included. When one Redis holds both cache and real data,
use a `volatile` policy and give every cache entry a TTL: then only cache entries are ever evicted.
:::
:::

:::step{type=try title="Look at the memory"}
```bash run
redis-cli INFO memory | grep -E "used_memory_human|maxmemory_human|maxmemory_policy"
```

```bash run
redis-cli SET test hello
```

`--bigkeys` samples every key and reports the biggest of each type, without blocking Redis:

```bash run
redis-cli --bigkeys
```

`MEMORY USAGE <key>` tells you how many bytes one key really takes.
:::

:::step{type=incident task=find_big_key minutes=15 title="Pager: Redis out of memory"}
**Brew Point on-call.** Redis refuses all writes: logins and orders are failing across every outlet.

Find the key that is eating the memory and **remove it**. Delete nothing else: the cache, the carts
and the sessions must stay.
:::

:::step{type=task task=eviction_policy title="Never refuse writes again"}
Change the eviction policy so that next time Redis fills up, it removes **cache entries** (keys with a
TTL) instead of refusing writes, and never touches keys without a TTL.

`CONFIG SET maxmemory-policy <policy>` changes it on the running server.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Redis holds only cache entries, every one with a TTL. Which policy lets it keep accepting writes when full?
:::
- [ ] `noeviction`
- [x] `volatile-lru` (or `allkeys-lru`)
- [ ] Any policy: Redis never fills up
:::explain
With `noeviction` Redis refuses writes when full. An LRU policy removes old cache entries to make room; when every key is a cache entry, `allkeys` and `volatile` behave alike.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is `redis-cli --bigkeys` safe on a busy server, while `KEYS *` is not?
:::
- [ ] It is not safe either
- [x] It walks the keys with SCAN in small steps, so other clients keep being served
- [ ] It only reads the first 100 keys
:::explain
`--bigkeys` uses `SCAN` under the hood. `KEYS *` walks every key in one go and blocks everyone until it finishes.
:::
:::

:::step{type=deep-dive title="Where the memory really goes"}
**Overhead per key.** Every key carries some 50 to 70 bytes of bookkeeping. A billion tiny keys cost
more in overhead than in data; grouping small values into hashes (`user:42` with fields) can save a
lot, because small hashes use a compact encoding.

**Fragmentation.** `mem_fragmentation_ratio` in `INFO memory` compares what the OS gave Redis with what
Redis uses. Far above 1.5 means wasted memory; Redis can defragment live (`activedefrag yes`).

**Eviction is approximate.** Redis does not sort all keys by age: it samples a few
(`maxmemory-samples`, default 5) and evicts the best candidate. Cheap, and close enough.

**Alert before 100%.** Eviction is a safety net, not a plan. Alert at about 80% of `maxmemory`.
:::

:::step{type=recap}
- `maxmemory` is Redis's budget; the eviction policy decides what happens at the limit.
- `noeviction` refuses writes; `allkeys-*` may delete anything; `volatile-*` only keys with a TTL.
- Find big keys with `redis-cli --bigkeys` and `MEMORY USAGE`, never by loading them.
- Give every cache entry a TTL, and keep real data out of reach of eviction.
:::
