:::step{type=story title="One server is a single point of failure"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Brew Point is opening forty more outlets. Two worries keep me up: if our one Redis server dies, every
outlet stops, and one server will not hold all our data for long. Redis answers the first with
replicas, and the second with Redis Cluster. Today we set up a replica for real, and prepare our keys
for a cluster.
:::

:::mission
Turn the second server into a live replica, and name a customer's keys so a cluster keeps them together.
:::
:::

:::step{type=concept title="Replicas: a live copy"}
A **replica** connects to the main Redis (the **primary**), copies the whole dataset once, then
receives every write as it happens. One command makes a server a replica:

```text
REPLICAOF <primary host> <port>
```

Replicas are **read-only** by default, so they are useful for reads (spreading load) and for safety
(a copy on another machine). Replication is **asynchronous**: the primary does not wait for
replicas, so a replica can be a few milliseconds behind.

**Sentinel** watches the primary and, if it dies, promotes a replica and tells clients where the new
primary is: automatic failover.

:::diagram{name="replication"}
Writes go to the primary, which sends each one on to its read-only replicas, a few milliseconds behind.
:::
:::

:::step{type=example title="Worked example: reading a replica's health"}
`INFO replication` on a replica tells you whether it is keeping up:

```text
> INFO replication
role:slave
master_host:redis
master_port:6379
master_link_status:up
master_last_io_seconds_ago:0
```

1. `role:slave` (the old word Redis still prints) means this server is a replica.
2. `master_host` and `master_port` show which primary it copies.
3. `master_link_status:up` is the line that matters: the copy is live.
4. `master_last_io_seconds_ago:0`: it heard from the primary this second.
:::

:::step{type=predict title="Guess first"}
:::question
Your app writes a new price to the primary, then immediately reads it from a replica. What can it see?
:::
- [ ] Always the new price: replicas are updated before the primary answers
- [x] Sometimes the old price: the replica may not have it yet
- [ ] An error: you cannot read from a replica
:::explain
Replication is asynchronous, so for a moment the replica can be behind (replication lag). Read your own
fresh writes from the primary, or use `WAIT` to block until replicas have them.
:::
:::

:::step{type=task task=replica_sync title="A live replica"}
A second Redis server runs as `replica`. Make it a replica of the main Redis (`redis`, port `6379`),
and check that it is connected and in sync.

```bash
redis-cli -h replica INFO replication
```
:::

:::step{type=concept title="Redis Cluster: data split across nodes"}
A **cluster** splits keys across several primaries using **16384 hash slots**: a key's slot is a
hash of its name, and each node owns a range of slots.

That breaks commands that touch **several keys** (a `MULTI`, a script, `SINTER`): the keys must be in
the same slot, or the cluster refuses.

**Hash tags** fix it. If a key contains `{...}`, only the part inside the braces is hashed:
`{customer:42}:cart` and `{customer:42}:wishlist` always share a slot, on the same node.

:::trace{title="which slot a key lands in (the real numbers)"}
| key | the part that is hashed | slot | note |
|---|---|---|---|
| customer:7:cart | the whole name | 10870 | Without a hash tag, every name lands somewhere different. |
| customer:7:wishlist | the whole name | 13267 | A different slot, maybe a different node: no multi-key commands. |
| {customer:7}:cart | customer:7 | 1721 | Only the part in braces is hashed. |
| {customer:7}:wishlist | customer:7 | 1721 | Same part, same slot, same node: they stay together. |
:::
:::

:::step{type=task task=hash_tags title="Keep a customer together"}
Create customer 42's **cart** (a hash with `filter coffee` = `2`) and **wishlist** (a set with `poha`),
with key names that end in `:cart` and `:wishlist`, chosen so a Redis Cluster would put **both in the
same slot**.

`redis-cli CLUSTER KEYSLOT <key>` only works on a cluster, so the check computes the slots for you.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You write to the primary and read from a replica one millisecond later. Is the new value guaranteed?
:::
- [ ] Yes, always
- [x] No: replication is asynchronous, so the replica may still be behind
- [ ] Only with Sentinel
:::explain
The primary answers your write before the replicas have it. Read your own fresh writes from the primary.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which pair of keys is guaranteed to share a slot in Redis Cluster?
:::
- [ ] `order:9:items` and `order:9:total`
- [x] `{order:9}:items` and `{order:9}:total`
- [ ] `items:{9}` and `total:9`
:::explain
With a hash tag, only the part in braces is hashed. Both keys hash `order:9`, so they share a slot.
:::
:::

:::step{type=deep-dive title="What you give up at scale"}
**Failover can lose writes.** A primary acknowledges a write, then dies before the replica got it; the
promoted replica never saw it. `WAIT 1 100` narrows the window, but asynchronous replication can
always lose a little.

**Split brain.** If the network splits, an isolated primary may keep accepting writes nobody will see.
`min-replicas-to-write` makes a primary refuse writes when it cannot reach its replicas.

**Hot keys do not scale out.** A cluster spreads *keys*, not *traffic on one key*. A single trending key
still hits one node: cache it in the app for a second, or split it into several keys.
:::

:::step{type=recap}
- `REPLICAOF host port` makes a live, read-only copy; replication is asynchronous.
- Sentinel promotes a replica when the primary dies.
- A cluster splits keys over 16384 slots; multi-key commands need keys in one slot.
- Hash tags (`{customer:42}:cart`) keep related keys in the same slot.
:::
