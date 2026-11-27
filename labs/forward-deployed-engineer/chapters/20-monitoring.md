:::step{type=story title="Live, and quiet"}
Claimdesk went live on Monday 2 November: drafts on the adjusters' screens, an adjuster accepting or changing each one.
The first days are quiet. Nobody complains. That is not the same as everything being fine.

Software that calls a model can get worse without any error message. The model provider can slow down. The emails can
change. A garage can start writing estimates differently. Nothing crashes; the drafts just quietly become less useful,
and the first person to notice is an adjuster, two weeks later, who has stopped trusting them.

Every request Claimdesk handles writes one line to its log (chapter 17's rules: no personal data). This chapter turns
that log into daily numbers, and the numbers into alerts.

The log for these two weeks is in `data/requests.jsonl`. It is a **simulation** built from real measurements: each line's
latency and token counts are those of one of the 109 real calls this course made through the gateway, picked at
random. Two things were added on purpose, so you can see what an alert looks like. You will find them.

:::mission
Turn a request log into daily numbers that matter (speed, errors, refers, cost), and raise alerts when they drift from
normal.
:::
:::

:::step{type=concept title="Which numbers to watch"}
One line of the log:

```json
{"day": "2026-11-02", "ms": 1311, "in": 343, "out": 48, "error": null, "draft": "refer", "amount_found": false}
```

From lines like this, five daily numbers answer the questions people will actually ask:

| Number | The question it answers | Who asks |
|---|---|---|
| `p50_ms`, `p95_ms` | Is it fast enough? | adjusters, IT |
| `error_pct` | Is it working? | IT |
| `refer_pct` | Is it saving work? | Meera |
| `no_amount_pct` | Are the emails still what we built for? | you |
| `cost_rs` | What does it cost? | finance |

Three of these are about the system. Two (`refer_pct`, `no_amount_pct`) are about the **inputs and the business**, and
they are the ones that catch quiet problems. A system can be fast, error-free and cheap while being useless.
:::

:::step{type=concept title="Percentiles, not averages" file="20-monitoring/monitor.py" line="18-21"}
Why "p95" instead of the average time?

Imagine 20 requests: 19 take 1.3 seconds and one takes 30 seconds (it timed out). The average is about 2.7 seconds,
which describes nobody's experience. The median (p50) is 1.3 seconds, the typical request. The p95 is the time that 95%
of requests beat: here, the slow one. **p95 tells you about the unlucky users**, and an adjuster who waits 30 seconds
for a draft remembers it.

`percentile` (already written) uses the **nearest-rank** method: sort the values; the p-th percentile is the value at
position ceil(p / 100 * n), counting from 1.

```text
values sorted: 900 1000 1200 1300 1500 1800 2000 2100 2600 9000      (n = 10)
p50: ceil(0.50 * 10) = 5th -> 1500
p95: ceil(0.95 * 10) = 10th -> 9000
```

Percentages of errors, refers and missing amounts are counted over **all** of a day's requests, rounded to one place.
Cost is the tokens priced exactly as in chapter 8 (input $0.15 and output $0.60 per million tokens, Rs 88 to the
dollar), rounded to paise.
:::

:::step{type=example title="Worked example: a day's numbers for a canteen till"}
This is only to read; it is not in your project. A till logs each sale; the manager wants a daily summary:

```python
from collections import defaultdict

def daily(sales):
    by_day = defaultdict(list)
    for s in sales:
        by_day[s["day"]].append(s)
    out = []
    for day in sorted(by_day):
        rows = by_day[day]
        n = len(rows)
        out.append({
            "day": day,
            "n": n,
            "p95_wait": percentile([r["wait_s"] for r in rows], 95),
            "card_pct": round(sum(1 for r in rows if r["card"]) / n * 100, 1),
        })
    return out
```

- `defaultdict(list)` creates an empty list the first time a day appears, so `append` always works.
- `sorted(by_day)` gives the days in order; ISO dates (`2026-11-02`) sort correctly as text.
- `sum(1 for r in rows if ...)` counts the rows that match.
:::

:::step{type=task task=daily_metrics title="Your turn: daily numbers"}
In `daily_metrics` in `monitor.py`:

1. Group the rows by `day`.
2. For each day, in date order, build `{"day", "n", "p50_ms", "p95_ms", "error_pct", "refer_pct", "no_amount_pct",
   "cost_rs"}`: percentiles of `ms`; the percent of rows with an `error`, with `draft == "refer"`, and without
   `amount_found`; and the cost of the day's tokens in rupees, rounded to 2 places.

Press **Check**.
:::

:::step{type=concept title="What counts as unusual" file="20-monitoring/monitor.py" line="32-37"}
A table of 14 days is good for a weekly review. Nobody reads it every morning. An **alert** reads it for you and speaks
only when something is unusual.

"Unusual" needs a definition. Ours, deliberately simple:

- **Baseline**: for each watched number, its average over the first 7 days (the first live week, which the adjusters
  were happy with).
- **Alert**: any later day where the number is more than **1.5 times** its baseline.

```text
refer_pct baseline 32.3    -> alert above 48.45
a day at 47.5               -> no alert
a day at 62.2               -> alert: ("2026-11-11", "refer_pct", 32.3, 62.2)
```

The factor is a trade-off. Too low (1.1), and normal day-to-day wobble raises alerts until people ignore them. Too high
(3), and real problems hide for days. Start somewhere sensible, look at what fires, and adjust, writing down why.
:::

:::step{type=task task=drift_alerts title="Your turn: drift alerts"}
In `drift_alerts`:

1. For each metric in `WATCH`, the baseline is the mean over `days[:baseline_days]`, rounded to 1 place.
2. For each day in `days[baseline_days:]`, and each metric in `WATCH` order, add `(day, metric, baseline, value)` when
   `value > factor * baseline`.

Press **Check**.
:::

:::step{type=try title="Two weeks of Claimdesk"}
```text
$ python monitor.py
day           n  p50 ms  p95 ms  err %  refer %  no amt %  cost Rs
2026-11-02   35    1311    1759    0.0     34.3      22.9     0.26
2026-11-03   39    1361    1910    5.1     30.8      20.5     0.28
2026-11-04   36    1400    1959    0.0     19.4      11.1     0.27
2026-11-05   42    1312    1612    2.4     19.0       9.5      0.3
2026-11-06   34    1301    1752    5.9     41.2      17.6     0.23
2026-11-07   34    1382    1700    5.9     38.2      29.4     0.23
2026-11-08   42    1298    1700    2.4     42.9      21.4      0.3
2026-11-09   39    1312    1759    2.6     38.5      17.9     0.29
2026-11-10   38    1519   10000    5.3     34.2      10.5     0.26
2026-11-11   45    1381    1759    0.0     62.2      51.1     0.33
2026-11-12   46    1304    1602    0.0     58.7      47.8     0.33
2026-11-13   46    1301    1759    0.0     65.2      56.5     0.34
2026-11-14   35    1304    1910    0.0     57.1      45.7     0.25
2026-11-15   35    1345    1729    0.0     68.6      54.3     0.26
alerts:
   2026-11-10 p95_ms: 10000 (usual 1770.3)
   2026-11-10 error_pct: 5.3 (usual 3.1)
   2026-11-11 refer_pct: 62.2 (usual 32.3)
   2026-11-11 no_amount_pct: 51.1 (usual 18.9)
   ...
```

Two different stories.

**10 November: the provider was slow.** The median barely moved (1,519 ms), but p95 hit **10,000 ms**, the timeout:
some calls never answered. The average would have hidden it; p95 did not. Those emails were referred to adjusters by
chapter 13's fallback, so nothing was lost, and the next day was normal. Action: note it, check the provider's status
page, and see whether it repeats.

**From 11 November: the emails changed.** Every day since, about half the emails have **no amount** (from 18.9% to
around 50%), and refers doubled. Speed and errors are perfectly normal; the system is "healthy". Reading a sample of the
emails shows why: one large garage network now sends its estimates as **PDF attachments**, and the emails just say
"estimate attached". Claimdesk reads email text, so it finds no amount, and correctly refers.

That second alert is the important one. No error, no crash, and the pilot's whole benefit was quietly halving. The fix is
not in your code: it is a conversation with Meera. Ask the garage network for the amount in the text? Or read PDF
attachments, which is a new feature with its own golden set and its own evals?

And cost: about **Rs 0.30 a day** for around 40 claims, roughly Rs 9 a month. Finance can stop worrying.
:::

:::step{type=history title="Telling a signal from noise"}
:::before{title="Before: every wobble was a reason to adjust"}
At Western Electric in the early 1920s, factories made telephone equipment by the million. Inspectors measured parts,
and every time a measurement moved, someone adjusted the machine. Often the adjustment made things worse, because the
movement had been ordinary variation, not a real change.
:::

On 16 May 1924 the physicist Walter Shewhart wrote a one-page memo with a new kind of chart. Plot each measurement over
time, draw limits computed from the process's normal variation, and act **only** when a point falls outside the limits.
Inside them is noise; leave it alone. Outside is a signal; find its cause. This was the first **control chart**, and the
start of statistical quality control.

Monitoring went further in the space programme. In NASA's Mission Control, flight controllers watched streams of
measurements from the spacecraft on their consoles, each with limits, and called out anything outside them.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-mission-control.webp" alt="Two flight controllers at their consoles in NASA's Mission Control in Houston, with screens of data in front of them, a world map on the left wall and a large screen showing parachutes during the Apollo 13 splashdown." credit="NASA Johnson Space Center" license="Public domain" source="https://commons.wikimedia.org/wiki/File:View_of_Mission_Control_Center_during_Apollo_13_splashdown_(S70-35471).jpg"}
Mission Control in Houston during the Apollo 13 splashdown, 17 April 1970.
:::

Your `drift_alerts` is a simple control chart: a baseline from normal days, a limit, and attention only for what falls
outside.

:::solved
Learn what normal variation looks like, and react only to what falls outside it.
:::

:::timeline
- **16 May 1924** Shewhart's memo introduces the control chart.
- **1931** Shewhart publishes *Economic Control of Quality of Manufactured Product*.
- **1960s** Mission Control monitors spacecraft against limits, live.
- **Today** Production software is watched through dashboards and alerts on percentiles, errors and business numbers.
:::

:::funfact
W. Edwards Deming, who later taught quality methods to Japanese industry after the Second World War, learned them from
Shewhart and called him the master.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
On 10 November the median latency barely moved but p95 jumped to 10,000 ms. What does that tell you?
:::
- [ ] Every request became slow
- [x] Most requests were normal, but a share of them were very slow or timed out
- [ ] The log is wrong
:::explain
The median describes the typical request; p95 describes the slow tail. A problem that hits some requests shows up in
the tail first.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
From 11 November, no errors, normal speed, and the refer rate doubled. Is Claimdesk broken?
:::
- [ ] Yes, the model got worse
- [x] No: the inputs changed (amounts moved into PDF attachments); Claimdesk correctly refers, and the business value drops
- [ ] Yes, the alert is wrong
:::explain
Watch business numbers, not just system numbers. The most important problems are often in the data, and the fix is a
conversation with the customer.
:::
:::

:::step{type=deep-dive title="Go deeper: monitoring model systems"}
**Small numbers flicker.** With 40 requests a day, one error is 2.5 points. That is why the error baseline here is
already 3.1%: a few rate-limit errors on ordinary days. Real alerting also asks for a minimum count, or for two bad
days in a row, before waking anyone.

**Watch quality, not just health.** Sample a few live emails each week, have an adjuster write the truth, and add them
to the golden set. Run the evals (chapter 15) on them: if accuracy on new emails falls, the world has moved.

**Watch the model too.** Providers update models behind the same name. Pin a dated model version where you can, and
rerun the evals when it changes.

**Tools.** Teams send these numbers to Prometheus and Grafana, Datadog, or a model-specific tool. LabBox itself exposes
its numbers at `/metrics` in the format Prometheus reads. The tool matters less than choosing the right numbers.

**Who gets the alert?** An alert nobody owns is noise. Decide, with the customer, who receives each one and what they
do. That list goes in the handover (chapter 21).
:::

:::step{type=recap}
You can now:

- choose the numbers that matter for a live model system: speed, errors, refers, the shape of the inputs, cost;
- compute daily p50 and p95 with nearest-rank percentiles, and explain why the tail matters;
- raise alerts against a baseline from normal days, and tune the factor knowingly;
- tell a system problem (a slow provider) from a data problem (the emails changed) by which numbers moved.

Next, chapter 21: you will leave Deccan Shield. Hand Claimdesk over so their team can run it, change it and trust it
without you.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-20-notes.webp" alt="Handwritten notes about monitoring: Watch speed, errors, refers, inputs, cost. p95 shows the unlucky users. Baseline from a normal week. Alert above 1.5 times the baseline. Slow provider: p95 hit the timeout. Emails changed: no amount, twice the refers." ai="true"}
One page of notes for this chapter.
:::
:::
