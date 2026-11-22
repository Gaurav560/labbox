:::step{type=story title="What does Redis keep, exactly?"}
In chapter 1 you measured how fast Redis is. Now let's look inside it.

Here is a question to keep in your head for this chapter: Basket's two stores, Kothrud and Baner, both count
today's orders in Redis. At lunchtime they each record an order **at the same moment**. Could the count end up one
short? With most ways of storing a number, it can. With Redis, used the right way, it never does. By the end of
this chapter you will know exactly why.

:::mission
Store your first keys, count orders without losing a single one, and tidy up after an old script.
:::
:::

:::step{type=concept title="A dictionary that lives on a server"}
If you have used a Python `dict`, you already understand the heart of Redis. It stores **keys**, each with a
**value**, and you ask for a value by its key:

```text
shop:name     ->  "Basket"
orders:today  ->  "128"
stock:eggs    ->  "120"
```

A **key** is a name you choose, like `shop:name`. A **value** is what is stored under it. The simplest kind of
value, and the one this chapter uses, is a **string**: a piece of text, which can also hold a number like `"128"`.

The difference from a Python `dict` is **where it lives**. A dict lives inside one running program and vanishes
when the program stops. Redis is a **server**, a program that runs on its own and waits for questions over the
network. Every program that can reach it shares the same dictionary: the Kothrud app, the Baner app, a background
worker, and you in your terminal.

:::diagram{name="redis-shared"}
Every store app and worker talks to the same Redis, which keeps everything in memory; Postgres keeps the full records on disk.
:::

Because Redis keeps the whole dictionary **in memory** (the RAM rung of chapter 1's ladder), a read or a write
takes a few microseconds of work. The rest of each round trip is the network.

**Check yourself:** two programs on two different machines both read `shop:name`. Do they see the same value?
(Yes: there is one Redis, and they both ask it.)
:::

:::step{type=try title="Your first conversation"}
`redis-cli` is a terminal for talking to Redis, already pointed at the lab's Redis server. You type a command;
Redis answers. `PING` is the "are you there?" of Redis:

```bash run
redis-cli PING
```

```text
PONG
```

Now store a value with **SET** and read it back with **GET**:

```bash run
redis-cli SET greeting 'Hello from Basket'
```

```text
OK
```

```bash run
redis-cli GET greeting
```

```text
"Hello from Basket"
```

The quotes around `Hello from Basket` were needed only because of the spaces: without them, Redis would think you
sent three separate words.

Now ask for a key that was never stored:

```bash run
redis-cli GET shop:phone
```

```text
(nil)
```

`(nil)` is how Redis says "there is no such key". It is not an error and not an empty string; it is "nothing".

Two small rules to notice. Commands are not case sensitive: `get` works as well as `GET`. **Keys are**:
`Shop:Name` and `shop:name` are two different keys.

Typing `redis-cli` before every command gets tiring. Type `redis-cli` on its own to open an interactive prompt,
then type commands one after another. `exit` leaves it. The lessons show interactive commands with a `>` in front.
:::

:::step{type=example title="Worked example: one key, from start to finish"}
Here is the whole life of a key, the way the interactive prompt shows it:

```text
> SET shop:phone '020 4455 6677'
OK
> GET shop:phone
"020 4455 6677"
> EXISTS shop:phone
(integer) 1
> DEL shop:phone
(integer) 1
> GET shop:phone
(nil)
```

Line by line:

1. `SET` stores the value under `shop:phone` and answers `OK`. If the key already existed, its old value is
   simply replaced.
2. `GET` reads it back, in quotes, because it is a string.
3. `EXISTS` answers with an **integer**: `1` for "it is there", `0` for "it is not".
4. `DEL` deletes it and answers how many keys it deleted: `1`.
5. `GET` now finds nothing: `(nil)`.

`DEL` can take several keys at once, and it tells you how many of them actually existed. `DEL a b c` on keys that
were never there answers `(integer) 0`, which is not an error: there was simply nothing to delete.
:::

:::step{type=task task=first_keys title="Your turn: introduce Basket"}
Store two facts about the shop, as plain text values:

| key | value |
|---|---|
| `shop:name` | `Basket` |
| `shop:city` | `Pune` |

Then read both back with `GET`, to see them with your own eyes. Press **Check**.
:::

:::step{type=concept title="One command at a time"}
Back to this chapter's question: two stores record an order at the same moment.

The obvious way to add one to a counter is three steps: **read** the number, **add** one in your program, **write**
the new number back. Watch what happens when two stores do that at the same time:

:::trace{title="two stores count an order at the same moment, the obvious way"}
| moment | Kothrud | Baner | orders:today | note |
|---|---|---|---|---|
| start |  |  | 128 | One order is about to be recorded in each store. |
| Kothrud reads | GET: 128 |  | 128 | Step one of the obvious way: read the number. |
| Baner reads |  | GET: 128 | 128 | Baner reads before Kothrud has written, so it also sees 128. |
| Kothrud writes | SET 129 |  | 129 | Kothrud adds one and writes 129. |
| Baner writes |  | SET 129 | 129 | Baner also writes 129. Two orders, but the counter moved by one. |
:::

One order has vanished. This is called a **race condition**: the result depends on the exact timing of two
programs, and a bad timing quietly gives a wrong answer. In a shop, wrong counts mean wrong stock and wrong money.

Redis has a command that does the read, the add and the write as **one** step:

```text
> INCR orders:today
(integer) 129
```

Nothing can slip in between the read and the write, because of the most important fact about Redis: **it runs one
command at a time, from start to finish.** Commands from every client wait in a single line, and each one runs
completely before the next one starts. Two `INCR`s from two stores simply run one after the other: 129, then 130.

:::diagram{name="one-at-a-time"}
Every command runs alone, start to finish; the next one waits its turn.
:::

That rule is also why each command must be quick. A command that took a whole second would make every other
client wait a whole second. You will meet that problem for real in chapters 13 and 17.
:::

:::step{type=predict title="Guess first"}
:::question
The key `visits` does not exist yet. What does `INCR visits` do?
:::
- [ ] It fails with an error: there is nothing to add to
- [x] It creates `visits` with the value 1
- [ ] It answers `(nil)` and changes nothing
:::explain
A missing key counts as 0, so `INCR` creates it and answers 1. That is why counters in Redis need no setup:
the first `INCR` makes them.
:::
:::

:::step{type=try title="Counters, live"}
Try the counter family yourself, in the interactive prompt. Here is what each one answered in this lab:

```text
> INCR visits
(integer) 1
> INCR visits
(integer) 2
> INCRBY visits 10
(integer) 12
> DECRBY visits 2
(integer) 10
> GET visits
"10"
```

- `INCR` adds one; `DECR` takes one away.
- `INCRBY` and `DECRBY` add or take away any whole number.
- Each answers the **new** value, so you never need a separate `GET` to know where the count stands.

Notice the last line: `GET` shows `"10"` in quotes. Redis stores the counter as a string; `INCR` just knows how
to treat a string of digits as a number. So what happens with a string that is not a number?

```text
> SET shop:name Basket
OK
> INCR shop:name
(error) ERR value is not an integer or out of range
```

An error, and the value is left exactly as it was. The same error appears if you try `INCRBY visits 2.5`: these
commands count in whole numbers. (For prices with decimals there is `INCRBYFLOAT`, though money is usually kept in
whole paise to avoid rounding trouble.)
:::

:::step{type=task task=cups_counter title="Your turn: the morning shift"}
Two jobs for the morning shift. The egg stock, `stock:eggs`, is already in Redis: `GET` it first to see how many
there are.

1. Three orders just came in. Record them in a counter called `orders:today`, one `INCR` per order.
2. One of the orders was a tray of **12 eggs**. Take 12 off `stock:eggs`, without typing the whole new number
   yourself (that would be the slow, racy "read, then write" way).

`GET` both keys afterwards to see the result. Press **Check**.
:::

:::step{type=concept title="Naming keys, and finding them again"}
Redis has no tables and no folders: just one big dictionary of keys. Real apps keep millions of keys tidy with a
**naming convention**: parts joined by colons, from general to specific.

```text
shop:name    customer:42    session:7f3a    stock:eggs    orders:2026-11-22
```

The colons mean nothing to Redis; they are for people. But they let everyone guess what a key holds, and they let
you find related keys by **pattern**. `*` in a pattern means "anything":

```bash run
redis-cli --scan --pattern 'stock:*'
```

`--scan` walks through the keys and prints the ones that match, a few at a time. There is also a command called
`KEYS` that does the same in one go (`KEYS 'stock:*'`). On your laptop it is handy. On a busy server it is
dangerous: it walks **every** key in one single command, and remember the rule, nothing else runs meanwhile. With
ten million keys, that is the whole shop frozen for a second or more. Use `--scan`, which works in small pieces
and lets other commands run in between. Chapter 17 shows the difference on a real slow server.

Two more commands you will use all the time:

- `TYPE key` says what kind of value a key holds. So far everything is `string`; chapter 4 brings others.
- `DBSIZE` says how many keys there are in total.
:::

:::step{type=task task=clean_up title="Your turn: tidy up after the import script"}
An old import script left temporary keys behind, all starting with `tmp:import:`. Find them and delete every one
of them. Leave everything else alone (the egg stock must survive).

Start by listing them:

```bash
redis-cli --scan --pattern 'tmp:*'
```

Then delete them; `DEL` takes several names at once. Scan again to make sure none are left. Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`EXISTS shop:email` answers `(integer) 0`. What does `GET shop:email` answer?
:::
- [ ] An error
- [x] `(nil)`
- [ ] `""`, an empty string
:::explain
A missing key reads as `(nil)`: not an error, not an empty string. Code that reads Redis must always be ready for
"not there"; in Python it arrives as `None` (chapter 6).
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `INCR` never lose a count, even when both stores use it at the same moment?
:::
- [ ] It locks the key for a second
- [x] Redis runs one command at a time, and `INCR` reads, adds and writes inside that one command
- [ ] It retries when two stores clash
:::explain
There is no gap between the read and the write for another client to slip into. The same one-at-a-time rule is
why one slow command delays everyone, so keep commands small.
:::
:::

:::step{type=deep-dive title="Go deeper: what a string really is, and SET's options"}
**Strings are bytes.** A Redis string can hold any bytes at all: text in any language, a number, JSON, even a small
image. The limit is 512 MB per value, though values over a few kilobytes are a warning sign in practice (chapter
14 shows why big values hurt).

**Numbers are stored cleverly.** When a string holds a whole number, Redis stores it as a real integer inside
(`OBJECT ENCODING stock:eggs` answers `"int"`), which saves memory and makes `INCR` fast.

**SET has options** that teams use every day:

- `SET key value NX` writes only if the key does **not** exist yet. It is the building block of the lock in
  chapter 11.
- `SET key value XX` writes only if the key **already** exists.
- `SET key value EX 60` gives the key a lifetime of 60 seconds. That is the whole of chapter 3.
- `SET key value GET` replaces the value and answers the old one, in one step.

**Several keys at once.** `MSET x 1 y 2` sets several keys in one command, and `MGET x y z` reads several,
answering `(nil)` for the ones that are missing. One command means one round trip, an idea chapter 6 builds on.
:::

:::step{type=recap}
You can now:

- explain Redis as one shared dictionary on a server, kept in memory;
- store, read, check and delete keys with `SET`, `GET`, `EXISTS` and `DEL`, and read `(nil)` correctly;
- count safely with `INCR`, `INCRBY` and `DECRBY`, and explain why Redis never loses a count;
- name keys with colons, and find them with `--scan` instead of `KEYS`.

Next, chapter 3: keys that expire on their own, for login codes and sessions.

:::photo{src="/lesson-images/redis/redis-02-notes.webp" alt="Handwritten notes about your first keys: SET key value / GET key; (nil) = no such key; INCR: read, add, write in one step; one command at a time; --scan, never KEYS" ai="true"}
One page of notes for this chapter.
:::
:::
