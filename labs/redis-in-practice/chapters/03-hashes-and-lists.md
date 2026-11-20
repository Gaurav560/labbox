:::step{type=story title="More than strings"}
:::character{name="Kabir" role="Backend lead, Brew Point"}
So far every value has been a single string. But our data has shape: a customer has a name, a
visit count and a loyalty tier; orders arrive one after another and must be made in that order.
Redis has a type for each of these, and choosing the right one is half of using Redis well.
:::

:::mission
Store the menu and a customer profile as hashes, and run the order queue on a list.
:::
:::

:::step{type=concept title="Hashes: a small object under one key"}
A **hash** is a key that holds many **fields**, each with its own value, like one row of a table or
a small dict:

```text
> HSET customer:42 name Asha visits 7
(integer) 2
> HGET customer:42 name
"Asha"
> HINCRBY customer:42 visits 1
(integer) 8
> HGETALL customer:42
1) "name"   2) "Asha"   3) "visits"   4) "8"
```

You can read or change one field without touching the others, and `HINCRBY` is the one-step counter
from chapter 1, for a single field.
:::

:::step{type=example title="Worked example: stock at one outlet"}
The Andheri outlet keeps its stock in one hash, one field per item:

```text
> HSET stock:andheri milk 12 beans 3
(integer) 2
> HINCRBY stock:andheri milk -2
(integer) 10
> HGET stock:andheri milk
"10"
> HGETALL stock:andheri
1) "milk"   2) "10"   3) "beans"   4) "3"
```

1. One `HSET` creates the hash with two fields, and answers how many fields were new.
2. Two litres of milk were used: `HINCRBY` with a negative number subtracts, in one step.
3. `HGET` reads one field; `HGETALL` reads the whole object, field and value in turn.
:::

:::step{type=predict title="Guess first"}
:::question
You want to store a customer's name, visits and tier. Which is the better design?
:::
- [ ] One string key holding JSON: `customer:42` -> `{"name": "Asha", "visits": 7}`
- [x] One hash: `customer:42` with the fields `name`, `visits` and `tier`
- [ ] Three keys: `customer:42:name`, `customer:42:visits`, `customer:42:tier`
:::explain
With JSON in a string, adding one visit means reading, parsing and writing the whole value back, and
two outlets doing that at once can lose an update. Three keys work, but scatter one customer
across many keys. A hash keeps the customer together and lets you change one field in one step.
:::
:::

:::step{type=task task=menu_hash title="The menu as a hash"}
Store the menu as **one hash** called `menu`, with one field per item:

| field | value |
|---|---|
| `filter coffee` | `30` |
| `cold coffee` | `40` |
| `vada pav` | `25` |

Field names with a space need quotes.
:::

:::step{type=task task=customer_profile title="A customer profile"}
Asha is customer 42. Create the hash `customer:42` with `name` = `Asha` and `visits` = `7`.

She has just walked in again: add one to her visits **without retyping the number**, then give her
the field `tier` with the value `gold`.
:::

:::step{type=concept title="Lists: things in order"}
A **list** is an ordered sequence of strings. You can push and pop at both ends, in one step:

```text
LPUSH orders:pending o1      add on the left
RPOP  orders:pending         take from the right
LRANGE orders:pending 0 -1   look at all of it, left to right
```

Push on one end and pop from the other, and you have a **queue**: first in, first out. Push and pop on
the same end, and you have a **stack**. Workers usually wait with `BRPOP`, which blocks until an item
arrives instead of asking again and again.

:::trace{title="a print queue: jobs in, the oldest out"}
| command | jobs, left to right | note |
|---|---|---|
| LPUSH jobs j1 | [j1] | The first job arrives on the left. |
| LPUSH jobs j2 | [j2, j1] | The newer job goes in front of it, on the left. |
| LPUSH jobs j3 | [j3, j2, j1] | The oldest job is now on the right. |
| RPOP jobs | [j3, j2] | RPOP takes from the right: j1, the oldest. First in, first out. |
:::
:::

:::step{type=task task=order_queue title="The order queue"}
The kitchen's queue is the list `orders:pending`. Three orders arrive, in this order: `o1`, `o2`, `o3`.
Add each one on the **left**.

Then the barista takes the **oldest** order off the queue. Afterwards, `LRANGE orders:pending 0 -1`
should show the two orders still waiting, newest first.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`HINCRBY customer:42 visits 1` runs while another app changes Asha's `tier`. What happens to `tier`?
:::
- [ ] It is overwritten by the old value
- [x] Nothing: `HINCRBY` changes only the `visits` field
- [ ] The command fails because the hash changed
:::explain
Hash commands work on single fields, so two apps can change different fields of the same customer
safely. That is the big advantage over storing the customer as one JSON string.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
You `LPUSH` new orders on the left. Which command takes the **oldest** order?
:::
- [ ] `LPOP`
- [x] `RPOP`
- [ ] `LRANGE 0 0`
:::explain
New items go in on the left, so the oldest is at the right end. Push on one end, pop from the other:
first in, first out. `LRANGE` only looks; it removes nothing.
:::
:::

:::step{type=deep-dive title="Why a list is not always the right queue"}
`RPOP` hands an order to a worker and removes it at the same moment. If that worker crashes before
the coffee is made, the order is simply gone.

The classic fix is `LMOVE orders:pending orders:in-progress RIGHT LEFT`: the order moves to a
second list in one step, and the worker removes it from there only when it is done. A crashed
worker leaves it behind for someone to retry.

For serious queues, Redis **streams** go further: consumer groups, acknowledgements and a record of
who is working on what. They come later in this course.
:::

:::step{type=recap}
- A hash keeps one object's fields under one key; `HSET`, `HGET`, `HGETALL`, `HINCRBY`.
- Prefer a hash to a JSON string when fields change on their own.
- A list keeps order: `LPUSH` plus `RPOP` is a first-in, first-out queue; `LRANGE 0 -1` shows it all.
- Popping removes work for good; `LMOVE` keeps it safe until it is done.
:::
