:::step{type=story title="The restart that ate the carts"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
On Sunday the Redis server was restarted for an operating system update. When it came back, every
customer's cart was empty and every loyalty counter was back to zero. Months ago someone switched
persistence off "to make Redis faster", and nobody remembered. Redis is in memory, but it does not
have to forget.
:::

:::mission
Turn durability back on: a write log for every change, and a fresh snapshot on disk.
:::
:::

:::step{type=concept title="Two ways to survive a restart"}
**RDB snapshots** write the whole dataset to one compact file, now and then (`BGSAVE`, or on a
schedule with the `save` setting). Fast to load, small, great for backups. A crash loses everything
since the last snapshot: maybe minutes.

**AOF, the append-only file**, logs every write as it happens. On restart Redis replays the log. How
often it is flushed to disk is `appendfsync`:

| appendfsync | you can lose |
|---|---|
| `always` | almost nothing, but every write waits for the disk |
| `everysec` | about one second of writes (the usual choice) |
| `no` | whatever the OS had not written yet |

Most production setups run both.

:::diagram{name="persistence"}
RDB saves now and then and loses the writes since the last snapshot; AOF logs every write and loses about a second.
:::
:::

:::step{type=example title="Worked example: is this server safe to restart?"}
Three commands tell you what a crash right now would cost:

```text
> CONFIG GET save
1) "save"   2) "3600 1 300 100 60 10000"
> CONFIG GET appendonly
1) "appendonly"   2) "no"
> INFO persistence
rdb_changes_since_last_save:4820
rdb_last_bgsave_status:ok
```

1. `save` is the snapshot schedule: here, after an hour with 1 change, 5 minutes with 100, or a
   minute with 10000.
2. `appendonly no`: there is no write log.
3. 4820 writes since the last snapshot: a crash now loses all of them. Turn AOF on, or snapshot now.
:::

:::step{type=predict title="Guess first"}
:::question
AOF is on with `appendfsync everysec`, and the server loses power. What is lost?
:::
- [ ] Nothing: every write is on disk
- [x] At most about the last second of writes
- [ ] Everything since the last RDB snapshot
:::explain
With `everysec`, Redis asks the disk to flush the log once a second, so a sudden power cut loses at
most about one second. `always` would lose nothing, at the price of waiting for the disk on every write.
:::
:::

:::step{type=try title="See what is on"}
```bash run
redis-cli CONFIG GET appendonly
```

```bash run
redis-cli INFO persistence | grep -E "aof_enabled|rdb_last_save_time|rdb_last_bgsave_status|rdb_changes_since_last_save"
```

`rdb_changes_since_last_save` is the number of writes a crash right now would lose.
:::

:::step{type=task task=aof_on title="Log every write"}
Turn on the append-only file, flushed to disk **once a second**. Both settings can be changed on the
running server with `CONFIG SET`.
:::

:::step{type=task task=fresh_snapshot title="A snapshot, now"}
Take a fresh RDB snapshot in the background, and make sure it succeeded.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
The last RDB snapshot was 10 minutes ago, and AOF is off. Redis crashes. What is lost?
:::
- [ ] Nothing
- [x] Every write from the last 10 minutes
- [ ] Only the last second
:::explain
Without AOF, the restart loads the last snapshot. Everything written since then is gone.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `BGSAVE` not stop Redis from serving clients while it writes the snapshot?
:::
- [ ] It does stop Redis
- [x] Redis forks a child process that writes the file while the main process keeps serving
- [ ] It saves only the keys nobody is using
:::explain
The fork gets a frozen copy of memory to write out, so the main thread carries on. `SAVE`, without the B, would block everyone.
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
- RDB: compact snapshots, fast restarts, but a crash loses everything since the last one.
- AOF: a log of every write; `everysec` risks about one second, `always` waits for the disk.
- `BGSAVE` snapshots in the background; `INFO persistence` shows what a crash would lose.
- Persistence is a setting someone can switch off: check it, and alert on it.
:::
