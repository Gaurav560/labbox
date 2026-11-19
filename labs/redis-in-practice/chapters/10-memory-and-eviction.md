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
