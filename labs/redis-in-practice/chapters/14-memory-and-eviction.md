:::step{type=story title="What happens when memory runs out?"}
Redis keeps everything in memory. That is the whole reason it is fast. But memory is finite, and it costs real
money: a gigabyte of RAM in the cloud costs many times more than a gigabyte of disk.

Everything Redis holds lives in modules like this one: very fast, but small and expensive. A server may have a few hundred gigabytes of memory, against many terabytes of disk.

:::photo{src="/lesson-images/redis/ram-module.webp" alt="A red memory module, a long thin circuit board with a red heat spreader, on a white background" credit="ElooKoN" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:RAM_Module_(SDRAM-DDR4).jpg"}
A DDR4 memory module.
:::

So every production Redis has a **budget**, and the interesting question is what happens at the edge of it. When
the budget is full and a customer adds rice to their cart, does Redis refuse? Does it throw something away to make
room? And if it throws something away, what?

Tonight that question is not theoretical. Basket's on-call phone has just gone off: Redis is refusing writes, and
customers cannot sign in or add anything to their carts.

:::mission
Find what filled Redis and remove it without freezing anything, then make sure a full Redis drops cache entries
instead of refusing real data.
:::
:::

:::step{type=concept title="A memory budget: maxmemory"}
Redis's budget is a setting called **maxmemory**: the most memory it may use for data. This lab's Redis was given
64 MB:

```text
> CONFIG GET maxmemory
1) "maxmemory"
2) "67108864"
```

67,108,864 bytes is exactly 64 MB (64 x 1024 x 1024). When Redis reaches that, what it does next is decided by a
second setting, the **eviction policy**, `maxmemory-policy`. **Eviction** means removing keys to make room. The
policies fall into three groups:

| Policy | When memory is full |
|---|---|
| `noeviction` | refuse every write that needs more memory, with an `OOM` error. Reads still work. |
| `allkeys-lru`, `allkeys-lfu`, `allkeys-random` | remove **any** key to make room |
| `volatile-lru`, `volatile-lfu`, `volatile-random`, `volatile-ttl` | remove only keys that **have a TTL** |

The last part of each name says **which** key goes first:

- **LRU**, least recently used: the key nobody has touched for the longest time.
- **LFU**, least frequently used: the key used the fewest times lately.
- **random**: any eligible key.
- **ttl** (volatile only): the key that would expire soonest anyway.

Now think about Basket's data. Cached prices and pages have a TTL, and losing one costs only a slower next read.
Carts, sessions and coin balances have no TTL, and losing one loses a customer's data. That difference is exactly
what the `volatile-` policies understand.

**Check yourself:** with `allkeys-lru`, could Redis evict a cart that nobody has touched for an hour? (Yes: under
`allkeys`, every key is a candidate.)
:::

:::step{type=example title="Worked example: how big is that key?"}
When memory is tight, the first job is to find out what is using it. Three tools, from the overview to one key:

**The overview**, `INFO memory`. A few of its lines, on a healthy server:

```text
used_memory_human:40.87M
maxmemory_human:64.00M
maxmemory_policy:noeviction
```

`used_memory_human` is what the data uses now; compare it with `maxmemory_human`.

**The biggest keys**, `redis-cli --bigkeys`. It walks all keys with `SCAN` (safely, in small steps) and reports
the biggest key of each type, plus totals. Its summary looks like this:

```text
Biggest   list found '"debug:log"' has 260000 items
Biggest   hash found '"cart:42"' has 2 fields
Biggest string found '"cache:page:34872"' has 1000 bytes
```

**One key's size**, `MEMORY USAGE key`, in bytes, including Redis's own bookkeeping for it:

```text
> MEMORY USAGE cache:page:1
(integer) 1080
```

A cached page of 1,000 characters costs about 1,080 bytes. Multiply by how many there are, and you know what the
cache costs.
:::

:::step{type=predict title="Guess first"}
:::question
A Redis with `maxmemory-policy noeviction` is full. A client runs `GET price:rice`, then `SET price:rice 60`.
What happens?
:::
- [ ] Both fail
- [x] The `GET` works; the `SET` fails with an OOM error
- [ ] Both work, and Redis grows past its budget
:::explain
`noeviction` refuses only commands that need more memory. Reads keep working, which is why a full Redis often
looks half alive: pages load, but nothing can be saved.
:::
:::

:::step{type=try title="Look at the incident"}
Open this chapter and its incident starts. Try writing anything:

```bash run
redis-cli SET lab:test ok
```

```text
(error) OOM command not allowed when used memory > 'maxmemory'.
```

That is what Basket's app sees on every login and every cart update. Now gather the facts, the way you would on a
real call. Memory:

```bash run
redis-cli INFO memory | grep -E "^(used_memory_human|maxmemory_human|maxmemory_policy):"
```

```text
used_memory_human:64.75M
maxmemory_human:64.00M
maxmemory_policy:noeviction
```

Full, slightly over, and with a policy that refuses. How many keys, and has anything been evicted?

```bash run
redis-cli DBSIZE
```

In this lab it answered `(integer) 36007`, and `INFO stats` showed `evicted_keys:0`: nothing can be evicted
under `noeviction`. Now find out **what** is filling it. You have the tools from the worked example.
:::

:::step{type=incident task=find_big_key minutes=15 title="Pager: Redis is out of memory"}
Customers cannot sign in or add to their carts. Find the key that is eating the memory, and remove it.

1. Find the biggest key (`redis-cli --bigkeys`) and confirm its size with `MEMORY USAGE`.
2. Decide whether it is real data or something that should never have grown like that.
3. Remove it **without freezing Redis**: a key this big takes a while to free, so use `UNLINK`, which frees it in
   the background, instead of `DEL`.

Do not delete anything else, and never run `FLUSHALL`: the carts must survive. When `SET lab:test ok` works again,
press **Check**.
:::

:::step{type=concept title="Never refuse writes again"}
You found it: a forgotten **debug log**, a list of 260,000 request lines that some code kept pushing to and nobody
ever trimmed. In this lab `MEMORY USAGE debug:log` answered `25659240`: 25 MB, nearly half the budget, in one key.
After `UNLINK debug:log`, `used_memory_human` fell to about 41 MB and writes worked again.

But the incident is not really over. The debug log was the trigger; the real weakness is the policy. The rest of
memory was full of cached pages, and they all have a TTL:

```text
> TTL cache:page:1
(integer) 7193
> TTL cart:42
(integer) -1
```

Cached pages can be thrown away at any time: the next read just rebuilds them. Carts cannot. So the right policy
for this Redis is one that evicts **only keys with a TTL**, the least recently used first: `volatile-lru`.

:::diagram{name="eviction-lru"}
With noeviction a full Redis refuses the write; with volatile-lru it removes an old cache entry and the write succeeds.
:::

Here is what that did in this lab. With `volatile-lru` set, 41,000 more cached pages were written, far more than
fit. Redis stayed at its budget, evicted old pages as needed, and the carts were untouched:

```text
used_memory_human:64.00M
evicted_keys:18951
```

18,951 old pages evicted, and `EXISTS cart:41 cart:42 cart:43 cart:44 cart:45` still answered `(integer) 5`.

One honest warning about `volatile-` policies: if memory fills up with keys that have **no** TTL (a real data
leak), there is nothing they are allowed to evict, and Redis refuses writes again, just like `noeviction`. That
is why the cache keys must always have a TTL, and why you watch memory.
:::

:::step{type=task task=eviction_policy title="Your turn: evict cache entries, never real data"}
Change this Redis's eviction policy so that when memory is full it removes **only keys with a TTL**, starting
with the least recently used.

Check it with `CONFIG GET maxmemory-policy`, then press **Check**. (The check refuses `noeviction`, and it also
refuses `allkeys-` policies, because they could evict carts and sessions.)
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Redis is used **only** as a cache: every key could be rebuilt from the database, and some cache keys have no TTL.
Which policy fits best?
:::
- [ ] `noeviction`
- [ ] `volatile-lru`
- [x] `allkeys-lru`
:::explain
When everything is a cache, any key may go, so `allkeys-lru` uses the whole budget well, including keys without a
TTL. `volatile-lru` would not touch those, and `noeviction` would refuse writes. The right policy depends on what
the Redis holds.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why did the incident use `UNLINK debug:log` rather than `DEL debug:log`?
:::
- [ ] `DEL` cannot delete lists
- [x] `DEL` frees all 260,000 items right away, holding up every other client; `UNLINK` removes the key at once and frees the memory in the background
- [ ] `UNLINK` keeps a backup copy
:::explain
Freeing a huge key is O(N) work. `UNLINK` unhooks the key instantly and lets a background thread do the freeing,
so nobody waits. Chapter 17 shows the difference in the slow log.
:::
:::

:::step{type=deep-dive title="Go deeper: where the memory really goes"}
**Overhead per key.** Every key costs more than its value: the key name, a small object header, its entry in the
main hash table, and a second entry if it has a TTL. That is why chapter 8 measured about 124 bytes for a price
whose value is two digits. Millions of tiny keys add up; grouping them into hashes can cut memory a lot (chapter
4's deep dive).

**Fragmentation.** `mem_fragmentation_ratio` in `INFO memory` compares what the operating system gave Redis with
what Redis uses. Around 1.0 to 1.5 is normal. Much higher means freed memory is scattered in small holes; Redis
can tidy it up with `CONFIG SET activedefrag yes`.

**Leave headroom.** Saving a snapshot (chapter 15) forks the Redis process, and pages that change during the save
are copied, so a busy Redis can briefly need noticeably more memory than `used_memory`. Teams set `maxmemory`
well below the machine's RAM, often around three quarters of it, so the server itself never runs out.

**LRU is approximate.** Redis does not keep all keys in a perfect "last used" order; that would cost too much
memory. It samples a few keys (5 by default, `maxmemory-samples`) and evicts the oldest of the sample. It is
close to true LRU, and far cheaper. LFU keeps a small, slowly decaying usage counter per key instead, which suits
caches where a few keys are always popular.

**Watch it.** Alert on `used_memory` approaching `maxmemory`, on `evicted_keys` climbing fast (the cache is too
small, so the hit rate falls), and on any `OOM` errors in the app's logs.
:::

:::step{type=recap}
You can now:

- explain `maxmemory` and the eviction policies, and what LRU, LFU and volatile mean;
- investigate a full Redis with `INFO memory`, `--bigkeys` and `MEMORY USAGE`;
- remove a huge key without freezing Redis, with `UNLINK`;
- choose a policy from what the data is: `volatile-lru` when real data and cache share a Redis, `allkeys-lru` for
  a pure cache.

Next, chapter 15: keeping data safe when Redis restarts.

:::photo{src="/lesson-images/redis/redis-14-notes.webp" alt="Handwritten notes about memory and eviction: maxmemory = the budget; noeviction refuses writes; volatile-lru evicts cache keys; --bigkeys, MEMORY USAGE; UNLINK, not DEL" ai="true"}
One page of notes for this chapter.
:::
:::
