:::step{type=story title="Table 7, twice"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
Our Bandra outlet takes evening table bookings in the app. On Saturday, two families arrived for
table 7 at 8 pm, both holding a confirmation. Two app servers each checked "is table 7 free?", both
saw yes, and both said yes. A script cannot fix this one: between the check and the booking, we call
another service. We need a lock that works across servers.
:::

:::mission
Make a booking that exactly one person wins, release locks safely, and explain where locks fail.
:::
:::

:::step{type=concept title="A lock is just a key"}
A **distributed lock** is a key that says "someone is working on this". Taking it is one command:

```text
SET lock:booking:table:7 <token> NX PX 2000
```

- `NX`: only if nobody holds it. You get `OK` (yours) or `nil` (someone else's).
- `PX 2000`: it expires after 2 seconds, so a crashed server cannot hold it forever.
- `<token>`: a random value only you know, like a `uuid4`. It proves the lock is still **yours**.

While you hold it, check and book. Then release it.
:::

:::step{type=predict title="Guess first"}
:::question
You hold a lock with a 2 second expiry, but your work takes 3 seconds. At second 2.5 another server takes the lock. At second 3 you run `DEL lock`. What happens?
:::
- [ ] Nothing: Redis knows it is no longer yours
- [x] You delete the other server's lock, and a third server can now take it too
- [ ] Redis returns an error
:::explain
`DEL` deletes whatever is there. Your lock expired, someone else took it, and you just removed theirs.
That is why the release must check the token first, and do the check and the delete as one step.
:::
:::

:::step{type=try title="Double booking, live"}
Thirty people try to book table 5 at the same moment:

```bash run
for i in $(seq 30); do curl -s -o /dev/null -w "%{http_code} " -X POST "localhost:8000/book/5?customer=c$i" & done; wait; echo
```

Every 200 is a family that was told the table is theirs.

```bash run
redis-cli DEL booking:table:5
```
:::

:::step{type=task task=book_once title="One table, one booking"}
Make `POST /book/{table}` safe across servers: when 30 people book the same table at the same moment,
**exactly one** gets a 200 and the table is stored for them; everyone else gets a **409**.

Use a lock per table, with a token and a short expiry.
:::

:::step{type=task task=safe_unlock title="Release only your own lock"}
`POST /locks/{name}/release` deletes `lock:<name>` no matter who holds it. Make it delete the lock
**only if its value is the token in the request**, as one atomic step.

The check takes a lock for `token-A`, asks your endpoint to release it with `token-B` (it must stay),
then with `token-A` (it must go).
:::

:::step{type=design title="Design review"}
Locks are where senior engineers earn their keep. Answer each in a few sentences, in your own words.

:::ask{id=lock_expiry}
Your lock expires after 2 seconds, but a slow booking takes 5. What can go wrong, and what would you do about it?
:::

:::ask{id=redis_failover}
Redis has a replica, and the main Redis crashes right after giving you a lock, before copying it to the replica. What can happen?
:::

:::ask{id=fencing}
A lock alone cannot stop a paused server from writing after its lock expired. What extra protection can the database give?
:::
:::

:::step{type=recap}
- A lock is `SET key token NX PX ms`: one owner, and it expires on its own.
- Release with a script that deletes only if the value is still your token.
- Locks have limits: expiry during slow work, failover, and paused processes.
- For correctness, pair locks with fencing tokens or a database constraint.
:::
