:::step{type=story title="How would you store a customer?"}
So far every value has been one plain string. That is enough for a name or a counter. But think about a customer
of Basket: a name, a number of orders, a loyalty tier, a phone number. Or the packing team's queue of orders,
waiting in the order they arrived. Neither is one string.

You could squeeze a customer into one string of JSON, `{"name": "Asha", "orders": 7}`. It works, until you want
to add one to `orders`. Then you must read the whole string, change it in your program, and write it all back:
the same read-then-write race you met in chapter 2.

Redis has a better answer. Besides strings, it stores **data structures**: values with a shape. This chapter
brings in two of them, **hashes** for things with fields, and **lists** for things in order.

:::mission
Put the catalogue in one hash, keep a customer profile you can update one field at a time, and run the order queue.
:::
:::

:::step{type=concept title="Hashes: a small object under one key"}
A **hash** is one key that holds many **field and value** pairs, like a small Python dict stored under a single
name. Here is the stock of the Baner store, three items under one key:

```text
> HSET stock:baner eggs 90 rice 40 dal 25
(integer) 3
> HGET stock:baner rice
"40"
```

`HSET` takes the key, then any number of field value pairs, and answers how many **new** fields it created: 3.
`HGET` reads one field. Every hash command starts with **H**, so they are easy to spot.

To see the whole hash, use `HGETALL`. It answers a flat list, field then value, field then value:

```text
> HGETALL stock:baner
1) "eggs"
2) "90"
3) "rice"
4) "40"
5) "dal"
6) "25"
```

Read it in pairs: eggs is 90, rice is 40, dal is 25. (In Python, chapter 6, the same command gives you a proper
dict.)

The real win is changing **one field** in one step. A tray of 12 eggs goes out:

```text
> HINCRBY stock:baner eggs -12
(integer) 78
```

No reading, no rewriting the other fields, no race. Here is the difference from the JSON way, side by side:

| | One string of JSON | One hash |
|---|---|---|
| Read one field | read the whole string, parse it | `HGET key field` |
| Add one to a number | read, parse, change, write it all back (racy) | `HINCRBY key field 1` (one step) |
| Add a field | rewrite the whole string | `HSET key field value` |

**Check yourself:** what does `HSET stock:baner atta 30` answer, if `atta` was not there before? (`1`: one new
field.)
:::

:::step{type=example title="Worked example: looking after one store's stock"}
A few more hash commands, on the same `stock:baner`. Here is what each answered in this lab:

```text
> HLEN stock:baner
(integer) 4
> HEXISTS stock:baner paneer
(integer) 0
> HGET stock:baner paneer
(nil)
> HDEL stock:baner dal
(integer) 1
> HKEYS stock:baner
1) "eggs"
2) "rice"
3) "atta"
> HMGET stock:baner eggs rice paneer
1) "78"
2) "40"
3) (nil)
```

1. `HLEN` counts the fields: 4 (eggs, rice, dal and the atta added earlier).
2. `HEXISTS` answers `0`: there is no paneer field.
3. `HGET` of a missing field answers `(nil)`, just like `GET` of a missing key.
4. `HDEL` removes a field (dal sold out) and answers how many it removed.
5. `HKEYS` lists the field names; `HVALS` would list the values.
6. `HMGET` reads several fields at once, with `(nil)` for any that are missing.

And one error every Redis user meets sooner or later:

```text
> GET stock:baner
(error) WRONGTYPE Operation against a key holding the wrong kind of value
```

`GET` is for strings, and this key holds a hash. Each command works on one type, and `TYPE stock:baner` (it
answers `hash`) tells you which one you have.
:::

:::step{type=predict title="Guess first"}
:::question
The key `catalogue` already holds a plain string. What does `HSET catalogue rice 60` do?
:::
- [ ] It turns the string into a hash with one field
- [ ] It adds the field next to the string
- [x] It fails with a WRONGTYPE error and changes nothing
:::explain
A key has exactly one type. Redis refuses to treat a string as a hash, so the command fails and the string stays.
To start again, `DEL catalogue` first, then `HSET`.
:::
:::

:::step{type=task task=menu_hash title="Your turn: the catalogue as a hash"}
Store three prices of Basket's catalogue, in rupees, in **one hash** called `catalogue`, using a single `HSET`:

| field | value |
|---|---|
| `rice` | `60` |
| `dal` | `120` |
| `mangoes` | `300` |

Check it with `HGETALL catalogue`, then press **Check**. If you get a WRONGTYPE error, the key already holds
something else: `DEL catalogue` and try again.
:::

:::step{type=task task=customer_profile title="Your turn: Asha's profile"}
Build Asha's customer profile as a hash, `customer:42`, and keep it up to date the Redis way:

1. Create it with two fields: `name` is `Asha` and `orders` is `7`.
2. Asha just placed another order. Add 1 to `orders` **without** writing the number yourself.
3. She has reached the gold tier: add a field `tier` with the value `gold`.

`HGETALL customer:42` should show name Asha, orders 8 and tier gold. Press **Check**.
:::

:::step{type=concept title="Lists: things in order"}
A **list** is a sequence of strings in a fixed order, like a Python list. You add to either end and take from
either end. L commands work on the **left** end (the front), R commands on the **right** (the back).

That makes a list a natural **queue**: new work goes in at one end, and workers take the oldest from the other.
Here, orders d1, d2 and d3 arrive in that order, pushed on the left:

```text
> LPUSH deliveries d1
(integer) 1
> LPUSH deliveries d2 d3
(integer) 3
> LRANGE deliveries 0 -1
1) "d3"
2) "d2"
3) "d1"
```

Each `LPUSH` answers the new length. `LRANGE key 0 -1` shows the list from the first position (0) to the last
(-1 means "the end"). The newest is on the left, the oldest on the right.

A packer takes the next job from the right, so the oldest order goes first:

```text
> RPOP deliveries
"d1"
> LRANGE deliveries 0 -1
1) "d3"
2) "d2"
```

**First in, first out**: d1 arrived first and left first. `LLEN deliveries` now answers `(integer) 2`, and
`RPOP` on an empty list answers `(nil)`.

:::trace{title='LPUSH d1, LPUSH d2 d3, then RPOP'}
| step | command | the list, left to right | note |
|---|---|---|---|
| 1 | LPUSH deliveries d1 | d1 | The list is created with one entry. |
| 2 | LPUSH deliveries d2 d3 | d3, d2, d1 | Each new entry goes in on the left. |
| 3 | RPOP deliveries | d3, d2 | The oldest, d1, comes out on the right. |
:::

Lists are also good for **"the last few"**: Basket's "recently viewed" row keeps a customer's last three items.
Push each view on the left, then trim the list to three:

```text
> LPUSH recent:42 eggs
(integer) 4
> LTRIM recent:42 0 2
OK
> LRANGE recent:42 0 -1
1) "eggs"
2) "mangoes"
3) "dal"
```

`LTRIM key 0 2` keeps positions 0 to 2 and throws the rest away, so the list never grows past three.
:::

:::step{type=task task=order_queue title="Your turn: the order queue"}
Run Basket's order queue, `orders:pending`:

1. Three orders arrive in this order: `o1`, then `o2`, then `o3`. Push them on the **left**, in one command.
2. The packing team takes the **oldest** order to pack. Take it out from the right.

`LRANGE orders:pending 0 -1` should now show the two orders still waiting, newest first: `o3`, `o2`. Press
**Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
You need to store a delivery rider's name, phone and current zone, and update the zone often. Which fits best?
:::
- [ ] Three separate string keys
- [x] One hash, `rider:17`, with three fields
- [ ] One list with three entries
:::explain
A hash keeps one thing's fields together under one key, and `HSET rider:17 zone baner` changes just one field.
A list would rely on positions (which entry is the phone?), and three keys are easy to get out of step.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
New jobs are added with `LPUSH jobs ...`. Which command takes the **oldest** job?
:::
- [ ] `LPOP jobs`
- [x] `RPOP jobs`
- [ ] `LRANGE jobs 0 0`
:::explain
`LPUSH` adds on the left, so the oldest entry sits at the far right. `LPOP` would take the newest (a stack, last
in first out), and `LRANGE` only looks without removing anything.
:::
:::

:::step{type=deep-dive title="Go deeper: waiting for work, and why a list is not always the right queue"}
**Workers that wait.** A worker that loops on `RPOP` wastes time asking an empty list again and again. `BRPOP`
**blocks**: it waits until something arrives, up to a timeout. Here a worker waited, and one second later
another client pushed a job:

```text
> BRPOP jobs 5
1) "jobs"
2) "j7"
```

It answers which list the job came from and the job itself. With `0` as the timeout it waits forever. Blocking
only affects that one connection; Redis keeps serving everybody else.

**Where list queues fall short.** When a worker takes a job with `RPOP` and then crashes, the job is gone: it left
the list and was never finished. There is `LMOVE` (move it to a "processing" list in one step) to keep a copy,
but there is no record of who is working on what, and no way for several teams to read the same jobs. Chapter 12's
**streams** solve exactly that, with consumer groups and acknowledgements.

**Hashes are compact.** A small hash (by default up to 128 fields with short values) is stored in a compact
encoding called a listpack, which uses far less memory than the same data in separate keys. Storing a million
small objects as hashes instead of a million separate string keys can save a lot of memory, which is exactly
what Instagram described doing in 2011 for hundreds of millions of photo IDs.
:::

:::step{type=recap}
You can now:

- store an object's fields in a hash with `HSET`, read them with `HGET`, `HMGET` and `HGETALL`;
- change one field in one safe step with `HINCRBY`, instead of rewriting a JSON string;
- run a first in, first out queue with `LPUSH` and `RPOP`, and keep "the last few" with `LTRIM`;
- recognise a WRONGTYPE error, and check a key's type with `TYPE`.

Next, chapter 5: sets for "who" and sorted sets for "who is on top".

:::photo{src="/lesson-images/redis/redis-04-notes.webp" alt="Handwritten notes about hashes and lists: HSET customer:42 name Asha; HINCRBY: one field, one step; LPUSH in, RPOP out = a queue; LTRIM keeps the last few; WRONGTYPE? check TYPE" ai="true"}
One page of notes for this chapter.
:::
:::
