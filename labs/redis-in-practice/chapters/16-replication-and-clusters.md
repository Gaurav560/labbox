:::step{type=story title="What if the Redis server itself dies?"}
Chapter 15 made Basket's data survive a restart. But a restart assumes the server comes back. What if the machine
itself fails: a dead disk, a broken network card, a whole cloud zone going dark? Then the data on its disk is out
of reach, and Basket's Redis is down until someone builds a new one. A system that stops when one machine stops
has a **single point of failure**.

Big websites run on rows of servers like these, in one of Wikimedia's data centres. With thousands of machines, some fail every week, so the systems are built so that one machine failing is an ordinary day, not an outage.

:::photo{src="/lesson-images/redis/wikimedia-servers.webp" alt="Tall racks of servers with rows of small blue and green lights, in a dark data centre aisle" credit="Victorgrigas" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Wikimedia_Foundation_Servers-8055_13.jpg"}
Servers in a Wikimedia data centre.
:::

And there is a second limit. One Redis server has one main thread and one machine's worth of memory. Basket is
growing: one day its data will not fit in one server's RAM, or its traffic will not fit in one thread.

Both problems are solved by using **more than one** Redis server, in two different ways: **replication** (more
copies of the same data) and **clustering** (the data split across servers). This chapter does the first for real,
and prepares your keys for the second.

:::mission
Turn the lab's second Redis server into a live copy of the first, and name customer 42's keys so a cluster keeps
them together.
:::
:::

:::step{type=concept title="Replicas: a live copy"}
A **replica** is a Redis server that keeps a copy of another one, the **primary** (older documents and Redis's own
output call them slave and master). The primary takes every write and sends a copy of it to each replica, a moment
later. Replicas are **read-only**: apps may read from them, but every write goes to the primary.

:::diagram{name="replication"}
Apps write to the primary; it sends every write on to its replicas, which apps can read from.
:::

What a replica gives you:

- **A spare that is ready.** If the primary dies, a replica already has (almost) all the data and can be promoted
  to be the new primary, in seconds instead of hours.
- **More reads.** Read-heavy work (dashboards, product pages) can be spread over several replicas, so the primary
  does less.
- **Backups without load.** Snapshots can be taken on a replica, so the primary never has to fork.

What it does not give you: more room for writes, or more memory. Every replica holds **all** the data, and every
write still goes through the one primary.

One important detail: replication is **asynchronous**. The primary answers the client first and sends the write to
replicas afterwards. Usually that is a millisecond or less, but if the primary dies at exactly the wrong moment,
its last few writes may never have reached the replica. Remember chapter 11's design review question about a lock
lost in a failover: this is why.
:::

:::step{type=example title="Worked example: reading a server's replication status"}
`INFO replication` tells you which role a server plays and how healthy its link is. The lab has two Redis
servers: `redis`, and a second one named `replica`, which so far is on its own. Asked directly (`-h replica`
points `redis-cli` at the second server), it said:

```text
# Replication
role:master
connected_slaves:0
```

`role:master` here only means "standalone": it is not copying anybody, and nobody is copying it. Once it becomes a
replica, the same command shows the link:

```text
role:slave
master_host:redis
master_port:6379
master_link_status:up
master_last_io_seconds_ago:2
```

1. `role:slave`: it is a replica.
2. `master_host` and `master_port`: whom it copies.
3. `master_link_status:up`: the link is working. `down` means it has lost contact and its data is getting older.
4. `master_last_io_seconds_ago`: seconds since it last heard from the primary; the primary pings regularly, so
   this stays small on a healthy link.

On the **primary**, the same command lists its replicas, with how far behind each one is:

```text
role:master
connected_slaves:1
slave0:ip=10.77.3.3,port=6379,state=online,offset=1,lag=1
```

`offset` counts the bytes of replication data sent, and `lag` is the seconds since that replica last
acknowledged. Watching the gap between the primary's offset and each replica's is how teams measure
**replication lag**.
:::

:::step{type=predict title="Guess first"}
:::question
The replica is connected and up to date. An app accidentally sends `SET shop:name x` to the **replica**. What
happens?
:::
- [ ] The write succeeds on the replica and is copied back to the primary
- [x] It is refused: a replica is read-only
- [ ] It succeeds on the replica only, and the two drift apart
:::explain
Replicas refuse writes by default (`replica-read-only yes`), so the copy can never drift from the primary.
:::
:::

:::step{type=try title="Make a copy, and watch it follow"}
`REPLICAOF host port` tells a server to become a replica of another one. Sent to the second server:

```text
$ redis-cli -h replica REPLICAOF redis 6379
OK
```

On that command, the replica connects to the primary, receives a full copy of its data, and from then on gets
every new write as it happens. In this lab, `shop:name` had been set on the primary before; a moment later the
replica had it too:

```text
$ redis-cli -h replica GET shop:name
"Basket"
$ redis-cli -h replica SET shop:name x
(error) READONLY You can't write against a read only replica.
```

Read from the copy: yes. Write to it: refused. (To turn a replica back into a standalone server, the command is
`REPLICAOF NO ONE`, which is also how a replica is promoted when its primary dies.)
:::

:::step{type=task task=replica_sync title="Your turn: a live replica"}
Make the lab's second server, `replica`, a live copy of `redis`:

1. Send it the command that makes it a replica of `redis` on port 6379 (use `redis-cli -h replica ...`).
2. Check its `INFO replication`: it should say `role:slave` and `master_link_status:up`.
3. Write any key on `redis`, and read it on `replica`.

Press **Check**: it writes a key of its own on the primary and waits for it to appear on the replica.
:::

:::step{type=concept title="Clusters: splitting the data"}
Replicas copy everything. When the data itself is too big for one server, or the writes too many for one primary,
you **split** the data across several primaries. That is **Redis Cluster**.

A cluster divides all possible keys into **16,384 slots**. Each primary owns a range of slots (say three
primaries with about 5,461 slots each), and each primary has its own replicas. The slot of a key is computed
from its **name**, with a checksum (CRC16) of the name, modulo 16384. In this lab, redis-py's own function
computed these:

```text
price:rice               slot 5072
price:dal                slot 12556
customer:42:cart         slot 10688
customer:42:wishlist     slot 6132
```

(`python3 -c "from redis.crc import key_slot; print(key_slot(b'price:rice'))"` prints one of them.)

Different names land in different slots, often on different servers. For most keys that is exactly the point:
the data spreads evenly. But it has a cost: **a command that touches several keys only works if they are all in
the same slot**. `MGET`, `SINTER`, a transaction or a Lua script over customer 42's cart **and** wishlist would
fail in a cluster, because slots 10688 and 6132 may live on different servers.

The fix is a **hash tag**. If a key name contains `{...}`, only the part **inside the braces** is used to compute
the slot:

```text
{customer:42}:cart       slot 4672
{customer:42}:wishlist   slot 4672
```

Same tag, same slot, same server, so commands across both keys work. Use tags for things that must be used
together (one customer's keys), and never one tag for everything: that would put all the data in one slot, on one
server, defeating the cluster.
:::

:::step{type=task task=hash_tags title="Your turn: keep customer 42 together"}
Customer 42 needs two keys that a cluster will always place together:

1. A **cart**, as a hash, with `rice` set to `2`. Its name must end in `:cart`.
2. A **wishlist**, as a set, containing `mangoes`. Its name must end in `:wishlist`.

Both names must contain `customer:42`, and they must land in the **same slot**. You can test a name with the
`key_slot` one-liner above. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Basket's Redis must survive the loss of one machine with almost no downtime. Which helps most?
:::
- [ ] A bigger server
- [x] A replica (with automatic failover), ready to be promoted
- [ ] A cluster with hash tags
:::explain
A replica already holds the data, so promoting it takes seconds. A cluster spreads data for size and write load;
its availability also comes from each primary having replicas.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
In a cluster, which two keys are guaranteed to be in the same slot?
:::
- [ ] `order:1` and `order:2`
- [ ] `customer:42:cart` and `customer:42:wishlist`
- [x] `{order:1}:items` and `{order:1}:status`
:::explain
Only the part inside the braces counts, and both use `order:1`. Without a tag, the whole name is hashed, so
similar names usually land in different slots.
:::
:::

:::step{type=deep-dive title="Go deeper: failover, Sentinel and managed Redis"}
**Who promotes the replica?** Something must notice that the primary is gone and promote a replica. Without a
cluster, that is **Redis Sentinel**: a few small Sentinel processes watch the primary, agree among themselves that
it is down (so one Sentinel's broken network cannot cause a false alarm), promote a replica, and tell clients the
new address. Inside Redis Cluster, the primaries themselves vote to promote a replica of a failed one.

**What can be lost.** Because replication is asynchronous, a failover can lose the last writes the old primary
acknowledged but had not yet sent. `WAIT 1 100` makes a client wait until at least one replica has a write (or 100
ms pass), which narrows the gap for writes that matter, at the cost of latency.

**Reading from replicas means reading slightly old data.** A customer who changes their address and reloads the
page from a replica might, for a millisecond or so, see the old one. Pages that must show your own latest write
usually read from the primary.

**Managed Redis.** Most teams do not run any of this by hand. Cloud services such as Amazon ElastiCache, Google
Memorystore and Redis Cloud run primaries, replicas, failover and backups for you. The ideas in this chapter are
still what you configure: how many replicas, cluster or not, and where.
:::

:::step{type=recap}
You can now:

- explain replicas, primaries and asynchronous replication, and what replicas do and do not give you;
- make a server a replica with `REPLICAOF`, and read its health in `INFO replication`;
- explain how a cluster splits keys into 16,384 slots by name;
- keep related keys together with hash tags, and know why one tag for everything is wrong.

Next, chapter 17, the capstone: production is slow, and you have the tools.

:::photo{src="/lesson-images/redis/redis-16-notes.webp" alt="Handwritten notes about replication and clusters: REPLICAOF redis 6379; replicas are read-only; replication is asynchronous; 16384 slots, by key name; (customer:42) = the same slot" ai="true"}
One page of notes for this chapter.
:::
:::
