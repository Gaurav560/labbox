:::step{type=story title="Should a login code live forever?"}
When you sign in to Basket, it texts you a four-digit code. You type it in, and you are in. Now think about that
code for a moment. Should it still work tomorrow? Next month? If someone finds your old message in a year, should
they be able to sign in as you?

Of course not. A login code should work for a few minutes and then **disappear by itself**. So should a
"remember me" session after a while, a cached price after a minute, a "too many attempts" block after an hour.
A surprising amount of data has a use-by date.

You could write a cleanup job that wakes up every minute and deletes old keys. Redis makes that unnecessary: any
key can carry its own timer, and Redis removes it when the timer runs out.

:::mission
Give a login code a 5 minute life, put a timer on a session that never ends, and rescue a promotion that is
about to vanish.
:::
:::

:::step{type=concept title="A key with a timer"}
Every key in Redis can have a **time to live**, a **TTL**: a number of seconds after which Redis deletes the key
on its own. You give it one when you store the key, with the `EX` option of `SET`:

```text
> SET otp:9999900000 7310 EX 120
OK
```

Read it as: store `7310` under `otp:9999900000`, and **expire** it in 120 seconds. Until then the key behaves like
any other key; `GET` reads it normally. Afterwards, it is simply gone, as if someone had run `DEL`.

Like the sand in an hourglass, a time to live only runs one way, and when it is out, the key is gone. Nobody has to come back and turn anything over.

:::photo{src="/lesson-images/redis/hourglass.webp" alt="A wooden hourglass with sand running from the top glass bulb into the bottom one" credit="S Sepp" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Wooden_hourglass_3.jpg"}
An hourglass: a timer that empties by itself.
:::

To see how much time a key has left, ask `TTL`:

```text
> TTL otp:9999900000
(integer) 117
```

117 seconds left: the clock started at 120 and has been running for three seconds. `TTL` has two special answers
you need to know by heart:

| TTL answers | It means |
|---|---|
| a positive number | the seconds left before the key expires |
| `-1` | the key exists and has **no** timer: it stays until someone deletes it |
| `-2` | there is **no such key** (it never existed, or it already expired) |

`PTTL` is the same, in milliseconds: `(integer) 116785`.

**Check yourself:** `TTL shop:name` answers `-1`. Will `shop:name` disappear on its own? (No: `-1` means no timer.)
:::

:::step{type=example title="Worked example: a code that expires while you watch"}
Let's watch a key die. This stores a code with a two second life, waits, and looks again:

```text
> SET code 1111 EX 2
OK
```

(two and a half seconds later)

```text
> GET code
(nil)
> TTL code
(integer) -2
```

1. `SET ... EX 2` stores the code with a 2 second timer.
2. After the timer runs out, `GET` finds nothing: `(nil)`.
3. `TTL` answers `-2`: there is no such key any more. Nobody ran `DEL`; Redis did it.

That is the whole trick behind login codes, sessions and caches. Your code never has to remember to clean up.

One small rule while we are here: the time must be positive. `SET x 1 EX 0` answers
`(error) ERR invalid expire time in 'set' command`.
:::

:::step{type=predict title="Guess first"}
:::question
`cart:9` was stored with `EX 600`, so its TTL is 600. Then someone runs `SET cart:9 dal`, with no `EX`. What does
`TTL cart:9` answer now?
:::
- [ ] 600 or a little less: the timer keeps running
- [x] `-1`: a plain SET replaces the key, timer included
- [ ] `-2`: the key was deleted
:::explain
`SET` replaces the **whole** key: the new value, and no timer, because none was given. This catches out real
teams: code that updates a cached value with a plain `SET` quietly makes it live forever. Add `EX` again, or use
`SET ... KEEPTTL` to keep the timer the key already had.
:::
:::

:::step{type=try title="Watch a timer, and break one"}
Let's see both behaviours for real. Store a cart with a ten minute timer and look at it:

```text
> SET cart:9 rice EX 600
OK
> TTL cart:9
(integer) 600
```

Now overwrite it with a plain `SET`, and look again:

```text
> SET cart:9 dal
OK
> TTL cart:9
(integer) -1
```

The timer is gone. This cart will now stay in Redis forever, which in a real shop means memory filling up with
carts nobody will ever check out. Put the timer back and try `KEEPTTL`:

```text
> SET cart:9 dal EX 600
OK
> SET cart:9 atta KEEPTTL
OK
> TTL cart:9
(integer) 600
```

`KEEPTTL` changed the value and kept the timer. Run `TTL cart:9` a few more times and watch it count down.
:::

:::step{type=task task=otp_expiry title="Your turn: a login code that expires"}
A customer with the phone number 9876543210 asked for a login code, and Basket sent **4821**.

Store the code under `otp:9876543210` so that it **expires in 5 minutes**, in a single command. Then check its
TTL: it should be counting down from 300.

If you take a long time and it expires before you press **Check**, just store it again.
:::

:::step{type=concept title="Timers on keys that already exist"}
Sometimes the key is already there and you only want to change its timer. Two commands do that without touching
the value:

```text
> EXPIRE cart:9 30
(integer) 1
> TTL cart:9
(integer) 30
```

`EXPIRE key seconds` gives an existing key a new timer (replacing any old one) and answers `1`. On a key that does
not exist it answers `0` and does nothing: `EXPIRE nothing 30` gives `(integer) 0`.

The opposite is `PERSIST`, which removes the timer and keeps the value:

```text
> PERSIST cart:9
(integer) 1
> TTL cart:9
(integer) -1
```

It answers `1` when it removed a timer, and `0` when there was none to remove (try it twice).

So there are two ways to give a key a timer, and the right one depends on the situation:

| You want to | Use |
|---|---|
| store a value **and** give it a timer | `SET key value EX seconds` |
| change only the timer of a key that exists | `EXPIRE key seconds` |
| keep the key forever after all | `PERSIST key` |
| change only the value, keep the timer | `SET key value KEEPTTL` |
:::

:::step{type=task task=session_ttl title="Your turn: end the endless session"}
Asha signed in at the Kothrud store, and her session was stored under `session:7f3a`. Look at it:

```text
> GET session:7f3a
"{\"customer\": 42, \"store\": \"kothrud\"}"
> TTL session:7f3a
(integer) -1
```

That `-1` is a bug: the session never expires, so Asha stays signed in forever, even on a shared phone.

Give the session a lifetime of **30 minutes**, without changing its value (do not `SET` it again). Check the TTL,
then press **Check**.
:::

:::step{type=task task=keep_forever title="Your turn: rescue the promo"}
The marketing team created a Diwali promotion, and then decided to keep it running for good. But it was stored
with a one hour timer:

```text
> GET promo:diwali
"20% off mangoes"
> TTL promo:diwali
(integer) 3596
```

Make `promo:diwali` permanent, keeping its value. `TTL promo:diwali` should answer `-1` afterwards. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`TTL otp:9876543210` answers `-2`. What does that tell you?
:::
- [ ] The code expires in 2 seconds
- [x] There is no such key: it expired, or it was never stored
- [ ] The key has no timer
:::explain
`-2` means "no such key". `-1` would mean "exists, no timer". A positive number is the seconds left.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your code refreshes a cached price every time it changes, with `SET price:rice 62`. The price was first cached
with `EX 60`. What happens?
:::
- [ ] The price expires 60 seconds after the first SET
- [ ] The price expires 60 seconds after the refresh
- [x] The price never expires: the plain SET removed its timer
:::explain
A plain `SET` replaces the timer with none. Always give `EX` again (or use `KEEPTTL`) when you update a key that
must expire.
:::
:::

:::step{type=deep-dive title="Go deeper: how Redis actually deletes expired keys"}
Redis does not keep a timer running for every key. With millions of keys that would be far too expensive. It
uses two simple tricks together.

**Lazy expiry.** Every time a command touches a key, Redis first checks its expiry time. If it is in the past,
Redis deletes the key right there and acts as if it was never there. That is why `GET code` answered `(nil)`
exactly on time.

**Active expiry.** Keys that nobody touches would otherwise stay in memory forever. So about ten times a second,
Redis picks a small random sample of keys that have a TTL and deletes the expired ones. If many in the sample
were expired, it samples again straight away. This keeps memory clean without ever doing one big, slow sweep
(remember: one command at a time, so no long pauses).

**What the numbers mean.** `INFO keyspace` shows how many keys there are and how many have a timer. In this lab,
after this chapter's commands, it showed:

```text
# Keyspace
db0:keys=5,expires=2,avg_ttl=1818813,subexpiry=0
```

Five keys, two of them with a timer, and an average time left of about 1.8 million milliseconds (half an hour).
A cache whose keys mostly have no timer is a memory leak waiting to happen.

**Expiry and replicas.** Replicas (chapter 16) never expire keys on their own; they wait for the main Redis to
send them a `DEL`. That keeps every copy consistent.
:::

:::step{type=recap}
You can now:

- give a key a lifetime with `SET ... EX`, and read its time left with `TTL` (`-1` no timer, `-2` no key);
- change the timer of an existing key with `EXPIRE`, and remove it with `PERSIST`;
- avoid the classic bug of a plain `SET` wiping a timer, with `EX` again or `KEEPTTL`;
- explain how Redis deletes expired keys: lazily on access, and actively in small samples.

Next, chapter 4: values with structure, hashes and lists.

:::photo{src="/lesson-images/redis/redis-03-notes.webp" alt="Handwritten notes about keys that expire: SET otp 4821 EX 300; TTL: -1 no timer, -2 no key; EXPIRE adds a timer; PERSIST removes it; a plain SET wipes the timer!" ai="true"}
One page of notes for this chapter.
:::
:::
