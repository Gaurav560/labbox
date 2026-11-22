:::step{type=story title="Something is failing, but what?"}
Tara has a public website: anyone can see tonight's targets, the latest sky images and the status of each dish, and
schools across Maharashtra use it in their science classes. This afternoon a teacher wrote to Anjali: "The site keeps
failing for my students. Sometimes it is just very slow."

The web server keeps an **access log**: one line for every request anyone made. Somewhere in its 400 lines from this
afternoon is the answer. The questions on-call engineers ask first are always the same three: **how many requests
failed? who is sending the most requests? which requests were slowest?** You will answer each one, then turn each answer
into a small script, so that next time it takes one command.

Why "log"? Sailors measured a ship's speed by throwing a piece of wood, a log, over the side on a knotted rope, and wrote
the speed into the **log book** every hour, with everything else that happened on board. A server's log is the same
idea: a diary written as things happen.

:::photo{src="/lesson-images/linux/ship-logbook.webp" alt="Two pages of a 1786 ship's log book, with dated handwritten entries in brown ink and small drawings of a coastline" credit="A. A. Buyskes" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Page_from_the_logbook_of_the_Dutch_warship_Medea_in_1786.jpg"}
The log book of the Dutch warship Medea, 1786.
:::

:::mission
Answer the three on-call questions from the access log, and save each answer as a script that works on any log.
:::
:::

:::step{type=concept title="Fields: every line has the same shape"}
Look at the first lines of the log:

```text
$ cd /workspace/05-logs
$ head -5 access.log
2026-11-19T12:00:00 10.0.0.31 POST /targets 200 32ms
2026-11-19T12:00:09 10.0.0.12 POST /status 200 306ms
2026-11-19T12:00:18 10.0.0.12 POST /status 200 52ms
2026-11-19T12:00:27 10.0.0.31 GET /sky 200 290ms
2026-11-19T12:00:36 10.0.0.31 POST /images 200 122ms
```

Every line has six **fields**, separated by spaces:

```text
2026-11-19T12:00:09  10.0.0.12  POST    /status  200     306ms
$1 time              $2 IP      $3 how  $4 page  $5 status  $6 duration
```

The **IP address** says which computer asked. The **status** is the server's answer, as a number with a meaning:

| Status | Means | Whose problem? |
|---|---|---|
| 2xx (200, 201) | success | nobody's |
| 3xx (302) | "look somewhere else" (a redirect) | nobody's |
| 4xx (404 not found) | the request was wrong | usually the visitor's |
| 5xx (500, 502, 503) | the server failed | **ours**: this is what wakes on-call engineers up |

The **duration** is how long the server took. Anything over a second feels broken to a person waiting.
:::

:::step{type=try title="grep: keep the lines you care about"}
`grep` prints the lines that contain some text. It is the most used tool on any server:

```text
$ grep /images access.log | head -3
2026-11-19T12:00:36 10.0.0.31 POST /images 200 122ms
2026-11-19T12:02:51 10.0.1.7 POST /images 200 363ms
2026-11-19T12:04:21 10.0.3.15 POST /images 200 289ms
$ grep -c /images access.log
58
$ grep -c " 404 " access.log
13
```

The options you will use every day:

| Option | Does | Example |
|---|---|---|
| `-c` | count the matching lines | `grep -c ERROR app.log` |
| `-v` | the lines that do **not** match | `grep -v " 200 " access.log` |
| `-i` | ignore upper and lower case | `grep -i post access.log` |
| `-n` | show line numbers | `grep -n /tonight access.log` |
| `-E` | a pattern, not just text | `grep -E " 5[0-9]{2} " access.log` |

That last one is a **regular expression**: `5[0-9]{2}` means a 5 followed by exactly two digits, so any status from
500 to 599:

```text
$ grep -E " 5[0-9]{2} " access.log | head -3
2026-11-19T12:00:45 10.0.1.7 POST /status 502 3263ms
2026-11-19T12:00:54 10.0.1.7 GET /sky 503 1090ms
2026-11-19T12:03:09 10.0.0.12 GET /sky 502 2841ms
```

Notice the spaces around `" 404 "`: without them, a duration like `1404ms` would match too. grep looks for text, not
for meaning. For meaning, there is a better tool.
:::

:::step{type=concept title="awk: a tool that understands columns"}
`awk` splits every line into fields, `$1` to `$6` here, and lets you test them and print them. Its programs go in single
quotes, in the shape `'condition {action}'`:

```text
$ awk '{print $2}' access.log | head -3
10.0.0.31
10.0.0.12
10.0.0.12
$ awk '$5 == 404' access.log | head -2
2026-11-19T12:09:27 10.0.2.9 GET /sky 404 69ms
2026-11-19T12:11:06 10.0.4.2 POST /targets 404 116ms
$ awk '$5 == 404 {print $4}' access.log | sort | uniq -c
      2 /login
      4 /sky
      1 /status
      3 /targets
      2 /targets/next
      1 /tonight
```

1. With only an action, `{print $2}` runs on every line.
2. With only a condition, `$5 == 404`, awk prints the lines where it is true.
3. With both: for the lines where the status is 404, print the page.

Conditions can compare numbers (`$5 >= 500`), and join with `&&` (and) and `||` (or). Unlike grep, `$5 >= 500` looks
at **the status field only**, so a duration can never be mistaken for a status.

:::diagram{name="linux-pipe"}
grep or awk keeps the lines, sort and uniq count them, head keeps the top: each tool one step of the pipeline.
:::

**Check yourself:** what does `awk '{print $4, $5}' access.log` print? (The page and the status of every request,
like `/targets 200`.)
:::

:::step{type=concept title="A script is just your pipeline, saved"}
Once a pipeline answers a question, save it as a **script**, so the next on-call person runs one command. A script is a
text file of commands. Open `count_5xx.sh`:

```text
$ cat count_5xx.sh
#!/usr/bin/env bash
# count_5xx.sh LOGFILE: print how many requests failed with a 5xx status (500 to 599). Just the number.
# TODO (task count_5xx): your pipeline here. It reads the log file given as "$1".
```

1. The first line, `#!/usr/bin/env bash`, says "run me with bash".
2. Lines starting with `#` are comments, for people.
3. `"$1"` is the **first argument**: when you run `bash count_5xx.sh access.log`, `"$1"` is `access.log`. Use
   `"$1"` and never a fixed name, and the script works on tomorrow's log too.

Run a script with `bash count_5xx.sh access.log`. Chapter 10 is all about scripts; this is all you need today.
:::

:::step{type=task task=count_5xx title="Your turn: how many failed?"}
Finish `count_5xx.sh`: it prints **just the number** of requests whose status is from **500 to 599**, for the log file
given as `"$1"`.

```bash
bash count_5xx.sh access.log
```

The check runs it on two logs it has never seen, so use `"$1"`, not `access.log`. Press **Check**.
:::

:::step{type=example title="Worked example: the status codes, ranked"}
Before the next two scripts, here is the "sort, count, sort by count" shape from chapter 4, on the status field:

```text
$ awk '{print $5}' access.log | sort | uniq -c | sort -rn
    282 200
     30 201
     21 500
     20 502
     19 503
     15 302
     13 404
```

In one line: 60 of 400 requests failed on the server's side (500, 502, 503), 15 percent. That alone explains the
teacher's email.

Swap `$5` for `$2` and the same pipeline ranks IP addresses instead, which is your next task. Add `head -3` for the top
three, and one more `awk '{print $2}'` at the very end to drop the counts and keep only the addresses.
:::

:::step{type=task task=top_ips title="Your turn: who is hammering us?"}
Finish `top_ips.sh`: it prints the **3 IP addresses with the most requests**, busiest first, one per line, and nothing
else (no counts).

```bash
bash top_ips.sh access.log
```

Press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
What does `sort -k6 access.log` sort by?
:::
- [ ] The whole line
- [x] The 6th field (the duration), but as text, so `100ms` comes before `1012ms` and `101ms`
- [ ] The 6th field, as a number
:::explain
`-k6` picks the field, but without `-n` sort compares text, character by character. As text, `1012ms` sorts before
`101ms`. `-n` makes it compare numbers, and it reads the number at the start of `306ms` as 306.
:::
:::

:::step{type=try title="Sorting by a field"}
See the difference `-n` makes:

```text
$ sort -k6 access.log | head -3
2026-11-19T12:15:36 10.0.0.12 GET /targets/next 200 100ms
2026-11-19T12:10:12 10.0.1.44 POST /targets 503 1012ms
2026-11-19T12:12:00 10.0.1.7 GET /sky 404 101ms
$ sort -k6 -n access.log | head -2
2026-11-19T12:04:57 10.0.3.15 POST /targets 200 10ms
2026-11-19T12:40:39 10.0.0.12 POST /images 200 11ms
```

As text, the order is nonsense. As numbers, the fastest requests come first. `-r` reverses it.
:::

:::step{type=task task=slowest title="Your turn: the slowest requests"}
Finish `slowest.sh`: it prints the **3 slowest requests**, the whole lines, slowest first.

```bash
bash slowest.sh access.log
```

Press **Check**.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is `awk '$5 >= 500'` safer than `grep 5` for finding failed requests?
:::
- [ ] awk is faster
- [x] awk tests only the status field; grep 5 matches a 5 anywhere, in times, addresses and durations
- [ ] grep cannot find numbers
:::explain
grep searches the whole line for text. awk understands fields, so it can ask exactly the question you mean.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Your script says `awk '$5 >= 500' access.log | wc -l`. What goes wrong tomorrow?
:::
- [ ] Nothing
- [x] It always reads today's `access.log`, whatever file you give it
- [ ] awk forgets the condition
:::explain
A fixed file name ignores the argument. `"$1"` uses whatever file the person running the script gives it.
:::
:::

:::step{type=deep-dive title="Go deeper: more awk, and where real logs live"}
**awk can do arithmetic.** `END` runs once, after the last line; `NR` is the number of lines read:

```text
$ awk '{sum += $6} END {print sum / NR " ms on average"}' access.log
556.438 ms on average
```

(awk reads `306ms` as the number 306.) Averages hide the worst cases, though: engineers watch the slowest 1 percent
(the "p99") as closely as the average, because those are the people who give up and leave.

**Where logs live.** On a real server: `/var/log/` holds the system's logs, web servers write to `/var/log/nginx/`
or `/var/log/apache2/`, and systemd keeps service logs that you read with `journalctl` (chapter 14).

**The cost of slow answers.** Studies by large shops have found that every extra tenth of a second of waiting loses a
noticeable share of visitors. An engineer who can find the slow requests in one minute instead of one hour saves
real money on every incident.

**Bigger tools.** At scale, logs from hundreds of servers are collected in one place (Elasticsearch, Loki, Splunk) and
searched with a query language. Underneath, the questions are exactly the ones you just asked.
:::

:::step{type=recap}
You can now:

- read a web server's access log: time, IP, method, page, status, duration, and what 2xx, 3xx, 4xx and 5xx mean;
- filter lines with `grep` (`-c`, `-v`, `-i`, `-n`, `-E`) and fields with `awk` (`'$5 >= 500'`, `{print $2}`);
- rank anything with "sort, count, sort by count, take the top", and sort by a field as a number (`sort -k6 -n -r`);
- save a pipeline as a script that reads its file from `"$1"`.

Next, chapter 6: finding any file, and any line of text, on a whole server.

:::photo{src="/lesson-images/linux/linux-05-notes.webp" alt="Handwritten notes about reading logs: 5xx = our fault; grep -c, -v, -i, -E; awk '$5 >= 500'; sort -k6 -n -r | head -3; scripts read '$1'" ai="true"}
One page of notes for this chapter.
:::
:::
