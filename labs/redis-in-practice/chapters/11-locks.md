:::step{type=story title="One rider, two customers"}
Basket delivers in slots: "today, 6 pm to 6:30 pm". Each slot has one rider, so each slot can be booked by
exactly one customer.

On a busy evening, Asha and Ravi both tap the 6 pm slot within the same few milliseconds. Both apps say "Your
slot is booked". At 6 pm, one rider has two deliveries on opposite sides of Pune, and one customer gets an angry
phone call.

The booking code checks "is this slot free?" before it books. It is the check-then-act gap from chapter 10 again,
but this time the "act" is not one number you can `DECRBY` in a script: it is a slow check that a rider is free,
then a write, possibly across several systems. What you need is a way to say: **while I am booking this slot,
nobody else may**. That is a **lock**.

Railways solved this problem in the 1870s. On a single track shared by trains in both directions, a driver may enter only while carrying a token taken from a machine like this Tyer's tablet instrument, and the machines at both ends make sure only one token is ever out. One token, one train: a lock.

:::photo{src="/lesson-images/redis/tablet-instrument.webp" alt="A green and red Victorian railway machine with a round brass top and a slot at the front where the tablet token comes out" credit="Sir Ross BA" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Tyer's_No._6_Tablet_Instrument.JPG"}
A Tyer's No. 6 tablet instrument, which hands out one token for a single track.
:::

:::mission
Make sure exactly one customer gets each slot, and that a request can only release its own lock.
:::
:::

:::step{type=try title="Double booking, live" file="11-locks/app.py" line="18-28"}
Look at `book()` in `11-locks/app.py`: check that the slot is not booked (line 24), check a rider (line 26, 50 ms),
store the booking (line 27). Start this chapter's app:

```bash run
cd /workspace/11-locks && uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

One customer at a time, it works:

```text
$ curl -X POST "localhost:8000/book/1900?customer=asha"
{"slot":1900,"booked_for":"asha"}
$ curl -X POST "localhost:8000/book/1900?customer=ravi"
{"detail":"Already booked"}
```

Now `book_race.py` sends thirty customers at the 6 pm slot (1800) at the same moment. Here are three runs in
this lab:

```bash run
python3 book_race.py
```

```text
told the slot is theirs: 4, told no: 26
the slot is stored for: c20
told the slot is theirs: 6, told no: 24
the slot is stored for: c26
told the slot is theirs: 3, told no: 27
the slot is stored for: c25
```

Four, six, three customers told "it is yours", and only one of them is actually stored: the last one to write.
Everyone else who was told yes will find out at 6 pm.
:::

:::step{type=concept title="A lock is just a key"}
A **lock** in Redis is nothing more than a key that means "taken", created with the `NX` option you used in
chapter 9 for the stampede:

```text
SET lock:booking:slot:1800 <token> NX PX 2000
```

- `NX`: create it only if it does not exist. Thirty requests send this at once; Redis runs them one at a time,
  so **exactly one** gets `OK` and holds the lock. The other 29 get `(nil)`.
- `PX 2000`: the lock's lifetime, in milliseconds (`PX` is the millisecond version of `EX`). If the holder
  crashes, the lock frees itself after 2 seconds instead of blocking the slot forever.
- `<token>`: a random value only the holder knows, such as a fresh UUID. You will see in a moment why the value
  matters.

The holder then does the real work (check the slot is still free, check a rider, write the booking) knowing
nobody else is doing the same, and finally **releases** the lock by deleting it. A request that did not get the
lock answers 409 straight away, "someone is booking this slot right now".

:::diagram{name="lock-flow"}
Exactly one SET NX succeeds; only that request books, then releases the lock if it still holds its token.
:::

Why is this a **distributed** lock? Basket runs many copies of its app on different servers. A Python lock
(`threading.Lock`) only works inside one process. A Redis lock works across every process and every server,
because they all ask the same Redis.
:::

:::step{type=example title="Worked example: one nightly report, with a release"}
Here is a complete lock on a different job: the nightly report from chapter 9, now with a proper token and a
release. This code is only to read; it is not in your project.

```python
token = uuid.uuid4().hex
if not r.set("lock:report", token, nx=True, px=600_000):
    return  # another worker has it
try:
    build_report()
finally:
    release(r, "lock:report", token)
```

1. `uuid.uuid4().hex` makes a random 32 character token, different for every attempt.
2. `r.set(..., nx=True, px=...)` takes the lock, or gives `None` if someone else holds it.
3. `try` / `finally` makes sure the lock is released even if `build_report()` raises an error. Without it, a crash
   would leave the lock until it expires, and the next worker would have to wait.
4. `release(...)` deletes the lock, but carefully, as the next steps explain.
:::

:::step{type=predict title="Guess first"}
:::question
Worker A holds `lock:report` with a 10 second lifetime, but its work takes 15 seconds. At second 10 the lock
expires and worker B takes it. At second 15, A finishes and runs a plain `DEL lock:report`. What happens?
:::
- [ ] Nothing: A's lock was already gone
- [x] A deletes **B's** lock, so a third worker can take it while B is still working
- [ ] Redis refuses, because the lock belongs to B
:::explain
A plain `DEL` does not know whose lock it is. A removes B's lock, and now B and a third worker C both believe
they hold it. That is why the lock's value is a token, and why release must check it.
:::
:::

:::step{type=task task=book_once title="Your turn: one slot, one booking"}
Make `book()` in `11-locks/app.py` safe:

1. Make a random token (`uuid.uuid4().hex`, which needs `import uuid`).
2. Take a lock on `lock:booking:slot:<slot>` with `NX` and a 2 second lifetime (`px=2000`). If you do not get it,
   raise a 409.
3. With the lock held, do the existing work: check the slot is free (409 if not), check the rider, store the
   booking.
4. Release the lock in a `finally` block. A plain `r.delete(lock)` is enough for now; the next task makes the
   release safe.

Run `python3 book_race.py`: it should tell exactly one customer yes, every time. Press **Check**.
:::

:::step{type=concept title="Release only your own lock" file="11-locks/app.py" line="35-41"}
Look at `release_lock()` on the right, an endpoint other Basket services use to release a lock they took. It
deletes the lock, whoever holds it. Here is what it did in this lab: worker A took `lock:report` with the token
`token-A`, and worker B, whose own lock had expired long ago, asked to release with `token-B`:

```text
$ redis-cli SET lock:report token-A EX 30
OK
$ curl -X POST localhost:8000/locks/report/release -H "content-type: application/json" -d '{"token": "token-B"}'
{"released":true}
$ redis-cli GET lock:report
(nil)
```

B removed A's lock. The fix is to delete the lock **only if its value is still your token**. But "check the
value, then delete" is two steps, and you know by now what happens in the gap between two steps: the lock could
expire and be taken by someone else right after your check. So it must be **one** step, which means a small Lua
script, exactly like chapter 10's:

```lua
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
```

It answers `1` when it deleted the lock (it was yours) and `0` when it did not (it was not yours, or it had
already expired). This compare-and-delete script is in the official Redis documentation for exactly this reason.
:::

:::step{type=task task=safe_unlock title="Your turn: release only your own lock"}
Make `release_lock()` safe:

1. Register the compare-and-delete script above with `r.register_script(...)`, near the top of the file.
2. In `release_lock()`, call it with `keys=[f"lock:{name}"]` and `args=[body.token]`.
3. Return `{"released": ...}`: `True` when the script deleted the lock, `False` otherwise.

Use the same script in `book()`'s `finally` too, with the token you made there. Try the token-B release again: the
lock should survive. Press **Check**.
:::

:::step{type=try title="Locked and safe"}
With both tasks done, the race in this lab, three times:

```text
told the slot is theirs: 1, told no: 29
the slot is stored for: c4
told the slot is theirs: 1, told no: 29
the slot is stored for: c13
told the slot is theirs: 1, told no: 29
the slot is stored for: c3
```

One customer told yes, and it is the customer actually stored. And the release:

```text
$ curl -X POST localhost:8000/locks/report/release -H "content-type: application/json" -d '{"token": "token-B"}'
{"released":false}
$ redis-cli GET lock:report
"token-A"
```

B's attempt changed nothing. When A releases with its own token, the answer is `{"released":true}` and the lock
is gone.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`SET lock:booking:slot:7 t1 NX PX 2000` answers `(nil)`. What does that mean?
:::
- [ ] You took the lock
- [x] Someone else holds the lock right now
- [ ] The lock expired
:::explain
`NX` writes only when the key is missing, so `(nil)` means it exists: another request is booking slot 7. Answer
409, or wait and try again.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does a lock need a lifetime (`PX 2000`) at all?
:::
- [ ] Redis requires it for `NX`
- [x] So that a holder that crashes or hangs cannot block everyone forever
- [ ] To make the booking faster
:::explain
Without a lifetime, a crashed holder leaves the lock in place until someone deletes it by hand, and the slot can
never be booked. With one, the worst case is a two second wait.
:::
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
You can now:

- explain why check-then-act across slow work needs a lock, and why a Redis lock works across many servers;
- take a lock with `SET key token NX PX ms`, and answer 409 when someone else holds it;
- release a lock safely with a compare-and-delete script, so you never remove someone else's lock;
- name the limits of a single Redis lock: expiry during slow work, failover, and paused processes.

That completes the app chapters for now. Next, chapter 12: streams, for orders that must never be lost.

:::photo{src="/lesson-images/redis/redis-11-notes.webp" alt="Handwritten notes about locks: SET lock token NX PX 2000; (nil) = someone else has it; release only your own token; always give it a lifetime; release in finally" ai="true"}
One page of notes for this chapter.
:::
:::
