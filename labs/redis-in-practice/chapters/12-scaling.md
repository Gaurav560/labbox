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
:::

:::step{type=task task=hash_tags title="Keep a customer together"}
Create customer 42's **cart** (a hash with `filter coffee` = `2`) and **wishlist** (a set with `poha`),
with key names that end in `:cart` and `:wishlist`, chosen so a Redis Cluster would put **both in the
same slot**.

`redis-cli CLUSTER KEYSLOT <key>` only works on a cluster, so the check computes the slots for you.
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
