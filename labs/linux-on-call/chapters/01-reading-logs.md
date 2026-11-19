:::step{type=story title="The pager goes off"}
:::character{name="Priya" role="Founder, Dabba Express"}
Our only server engineer is on leave and the pager just went off: "error rate high". There is no
dashboard, just the log. Every on-call engineer reads logs from the terminal, and today that is you.
:::

:::mission
Answer three on-call questions from the log with small shell tools, and keep them as scripts for next time.
:::
:::

:::step{type=concept title="Fields and pipes"}
Each line in `access.log` is one request, split into **fields** by spaces:

```text
2026-11-19T12:00:09 10.0.0.12 GET /menu 200 35ms
$1                  $2        $3  $4    $5  $6
```

`awk` works on fields: `awk '{print $2}' access.log` prints the second field of every line, and
`awk '$5 == 404' access.log` prints only the lines where the fifth field is 404.

A **pipe** `|` sends the output of one command into the next, so small tools add up:

```bash
awk '{print $4}' access.log | sort | uniq -c
```

Inside a script, `$1` is the first argument, the file you pass in.
:::

:::step{type=predict title="Guess first"}
:::question
A file has the lines `b`, `a`, `b`. What does `uniq -c file` print?
:::
- [ ] `2 b` and `1 a`
- [x] `1 b`, `1 a`, `1 b`
- [ ] `1 a` and `2 b`
:::explain
`uniq` only merges lines that sit **next to each other**. That is why you almost always `sort`
first: `sort file | uniq -c` gives `1 a` and `2 b`.
:::
:::

:::step{type=try title="Look at the log"}
```bash run
head -5 access.log
```

```bash run
awk '{print $5}' access.log | sort | uniq -c | sort -rn
```

That second line counts requests per status code, most common first. Read it from left to right:
take field 5, sort, count repeats, sort by count.
:::

:::step{type=task task=count_5xx title="How many failed?"}
Make `count_5xx.sh` print **just the number** of requests with a status from **500 to 599**.

```bash
bash count_5xx.sh access.log
```

The check runs it on other logs too, so read the file given as `$1`.
:::

:::step{type=task task=top_ips title="Who is hammering us?"}
Make `top_ips.sh` print the **3 IP addresses with the most requests**, busiest first, one IP per
line and nothing else.
:::

:::step{type=task task=slowest title="The slowest requests"}
Make `slowest.sh` print the **3 slowest requests**, the whole lines, slowest first.
:::

:::step{type=recap}
- `awk '{print $N}'` picks a field; `awk '$5 >= 500'` keeps matching lines.
- `sort | uniq -c | sort -rn` is the classic "count and rank" pipeline.
- `sort -k6 -n -r` sorts by a field as a number, biggest first; `head` keeps the top.
- Scripts take the file as `$1`, so they work on tomorrow's log too.
:::
