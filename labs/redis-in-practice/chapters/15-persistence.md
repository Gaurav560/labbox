:::step{type=story title="What survives a restart?"}
Redis keeps everything in memory, and memory forgets. When a server reboots for a security update, when the
process crashes, when the power goes, everything in RAM is gone in an instant.

For a pure cache that is fine: it fills up again from the database. But Basket's Redis also holds carts, login
sessions and coin balances, and some of those exist nowhere else. A restart that loses them means customers
signed out, carts emptied, coins vanished.

So Redis can also write its data to **disk**, in the background, so that a restarted Redis comes back with its
data. This is called **persistence**, and there are two very different ways to do it. Choosing between them is a
trade-off between speed, safety and disk space, and today you see both, and a restart that loses everything.

Aircraft solved the same problem with the flight data recorder: it writes down everything that happens during a flight, as it happens, inside a box built to survive a crash. Redis's append-only file is the same idea for data.

:::photo{src="/lesson-images/redis/flight-recorder.webp" alt="A bright orange flight data recorder box with French writing on it that says flight recorder, do not open" credit="NTSB" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Fdr_sidefront.jpg"}
A flight data recorder: everything written down as it happens.
:::

:::mission
Log every write to disk, flushed every second, and take a fresh snapshot after persistence was switched off.
:::
:::

:::step{type=concept title="Two ways to remember: snapshots and a log"}
**RDB snapshots.** Every so often Redis writes a complete copy of its data to one compact file, `dump.rdb`. It
is like taking a photo of memory. A restarted Redis loads the photo, which is fast. The catch: everything written
**after** the last photo is lost in a crash. With a snapshot every five minutes, a crash can lose up to five
minutes of writes.

**AOF, the append-only file.** Redis appends **every write command** to a log file as it happens. A restarted Redis
replays the log from the start and ends up exactly where it was. Much less is lost in a crash, but the log is
bigger than a snapshot and slower to replay, so Redis compacts it now and then (rewriting it as a snapshot plus
the latest commands).

How much is lost with AOF depends on how often the log is pushed all the way to the disk, which is a separate
step called **fsync** (the operating system otherwise holds writes in memory for a while). The setting is
`appendfsync`:

| appendfsync | Pushed to disk | A crash can lose | Cost |
|---|---|---|---|
| `always` | after every write | almost nothing | every write waits for the disk: much slower |
| `everysec` | once a second | about one second of writes | small; the usual choice |
| `no` | when the operating system decides | up to about 30 seconds | smallest |

:::diagram{name="persistence"}
RDB takes a snapshot now and then and loses what came after the last one; AOF logs every write and loses at most about a second.
:::

Many teams run **both**: AOF for minimal loss, and RDB files copied off the server as backups. You can check
what is on with `CONFIG GET appendonly` (AOF) and `CONFIG GET save` (the snapshot schedule; an empty value means no
automatic snapshots).

**Check yourself:** with `appendfsync everysec`, the server loses power. Roughly how much can be lost? (About the
last second of writes.)
:::

:::step{type=example title="Worked example: is this server safe to restart?"}
Before restarting any Redis, an engineer checks what will survive. `INFO persistence` holds the answer. Here are
its key lines on a server where persistence is on and a snapshot was just taken:

```text
rdb_changes_since_last_save:0
rdb_last_save_time:1795356316
rdb_last_bgsave_status:ok
aof_enabled:1
aof_last_bgrewrite_status:ok
```

Read them like a checklist:

1. `aof_enabled:1`: the append-only file is on, so every write is logged.
2. `rdb_last_bgsave_status:ok`: the last snapshot succeeded. If this says `err`, the disk may be full, and you
   must not restart until you know why.
3. `rdb_last_save_time`: when that snapshot finished, in seconds since 1970. Compare it with `LASTSAVE`, which
   gives the same number, or with the current time.
4. `rdb_changes_since_last_save:0`: no writes since the snapshot, so even the snapshot alone is complete.

On a server with **everything off**, the same lines would show `aof_enabled:0`, a growing
`rdb_changes_since_last_save` and an old `rdb_last_save_time`: a restart would lose every change since then.
:::

:::step{type=predict title="Guess first"}
:::question
Persistence was switched off at runtime with `CONFIG SET appendonly no` and `CONFIG SET save ""`. A cart is
added, then Redis restarts. Is the cart still there?
:::
- [ ] Yes, Redis always saves on shutdown
- [x] No: nothing wrote it to disk, so the restarted Redis does not know it ever existed
- [ ] Only if the cart had a TTL
:::explain
With both off, the cart lived only in memory. The next step shows exactly that happening.
:::
:::

:::step{type=try title="See what is on, and what a restart loses"}
Open this chapter, and its setup does what someone did "to make Redis faster": it switches off both kinds of
persistence. Look:

```text
> CONFIG GET appendonly
1) "appendonly"
2) "no"
> CONFIG GET save
1) "save"
2) ""
```

No append-only file, and no snapshot schedule. And `INFO persistence` agreed: `aof_enabled:0`, with
`rdb_changes_since_last_save` counting up every write that nothing has saved.

Here is what happened when this lab's Redis was then restarted, after a cart was added:

```text
> HSET cart:42 rice 2 dal 1
(integer) 2
> DBSIZE
(integer) 2
```

(the Redis server restarts)

```text
> DBSIZE
(integer) 0
> HGETALL cart:42
(empty array)
```

Everything gone. Notice one more thing that happened after the restart:

```text
> CONFIG GET appendonly
1) "appendonly"
2) "yes"
```

The restarted Redis read its settings from its start-up options, which say `appendonly yes`. `CONFIG SET` changes
a **running** server only; it is forgotten at the next restart unless it is also written to the config file. That
cuts both ways: the "make it faster" change did not last, but neither will your fix, unless it is saved too
(`CONFIG REWRITE` writes the running settings back to `redis.conf`).

(You cannot restart the lab's Redis yourself, so this restart was run once, by us, on the same setup.)
:::

:::step{type=task task=aof_on title="Your turn: log every write"}
Turn the append-only file back on, flushed to disk **once a second**:

1. Switch on `appendonly`.
2. Set `appendfsync` to the setting that pushes the log to disk every second.

Check both with `CONFIG GET`, then press **Check**.
:::

:::step{type=concept title="Snapshots without stopping: BGSAVE"}
A snapshot of a big Redis can take seconds to write. If Redis stopped serving while it wrote, every snapshot
would be an outage. So it does something clever. `BGSAVE` (background save) **forks** the Redis process: the
operating system makes a child process that shares the parent's memory as it was at that instant. The child
writes that frozen picture to `dump.rdb`, while the parent carries on serving clients as usual.

```text
> LASTSAVE
(integer) 1795356305
> BGSAVE
Background saving started
```

A second later:

```text
> LASTSAVE
(integer) 1795356316
```

`LASTSAVE` moved on: a new snapshot is on disk. (`SAVE`, without the B, writes the snapshot in the main process
and blocks every client until it is done. Do not use it on a live server.)

Here is the price of the fork, from `INFO persistence` after that save:

```text
rdb_last_cow_size:512000
```

**COW** is copy-on-write: when the parent changes a page of memory while the child is still writing, the operating
system must copy that page first, so both can see their own version. Here only 512,000 bytes (half a megabyte)
had to be copied. On a big, busy Redis this can be gigabytes, which is why chapter 14 said to leave memory
headroom.

After this lab's Redis was restarted with persistence on, the cart was still there, and its disk held both files:
`dump.rdb` and the `appendonlydir` folder. The end of the append-only file shows exactly what it logs, the
command itself:

```text
HSET
$7
cart:42
$4
rice
```

That is the command in Redis's own wire format (each `$7` says "the next word has 7 bytes"). Replaying the file
means running these commands again, in order.
:::

:::step{type=task task=fresh_snapshot title="Your turn: a snapshot, now"}
Persistence was off, so the newest snapshot on disk is old, and everything since is unprotected. Take a fresh
snapshot **without blocking** Redis, and confirm it finished: `LASTSAVE` should show a time from a moment ago, and
`INFO persistence` should say `rdb_last_bgsave_status:ok`. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does `BGSAVE` not stop Redis from serving clients while it writes the snapshot?
:::
- [ ] It does stop Redis
- [x] Redis forks a child process that writes the file while the main process keeps serving
- [ ] It saves only the keys nobody is using
:::explain
The child gets a frozen copy of memory to write out, so the main thread carries on. `SAVE`, without the B, would
block everyone.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You fixed the persistence settings with `CONFIG SET`. What else must you do so they survive the next restart?
:::
- [ ] Nothing, `CONFIG SET` is permanent
- [x] Write them to the config file, for example with `CONFIG REWRITE`
- [ ] Run `BGSAVE`
:::explain
`CONFIG SET` changes only the running server. The restart in this chapter showed it: the start-up options won.
`BGSAVE` saves data, not settings.
:::
:::

:::step{type=design title="Design review"}
Durability is a trade-off you choose on purpose. Answer each in a few sentences.

:::ask{id=rdb_vs_aof}
Why would a team run both RDB snapshots and AOF, instead of only one of them?
:::

:::ask{id=fsync_always}
A payments team asks for `appendfsync always`. What do they gain, what does it cost, and is Redis the right place for that data?
:::
:::

:::step{type=recap}
You can now:

- explain RDB snapshots and the append-only file, and what each loses in a crash;
- choose an `appendfsync` setting from how much loss is acceptable, and know why `everysec` is the usual one;
- check whether a server is safe to restart from `INFO persistence`;
- take a snapshot without blocking with `BGSAVE`, and make settings survive a restart with `CONFIG REWRITE`.

Next, chapter 16: a second Redis that copies the first, and spreading data over many servers.

:::photo{src="/lesson-images/redis/redis-15-notes.webp" alt="Handwritten notes about persistence: RDB: a snapshot now and then; AOF: every write logged; everysec: lose about 1 second; BGSAVE forks, no waiting; CONFIG REWRITE keeps settings" ai="true"}
One page of notes for this chapter.
:::
:::
