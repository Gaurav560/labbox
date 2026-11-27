:::step{type=story title="Half the batch came back empty"}
Remember chapter 9's first real batch: 30 emails sent as fast as the code could send them, and **15 came back as
`RateLimitError`**. The gateway allows 20 requests a minute per user; the batch asked for 30 in a few seconds.
`safe_extract` set the failures aside instead of crashing, which was right, but half the work was not done.

At Deccan Shield the same thing will happen in production, at the worst moment: Monday morning, when the weekend's
claims arrive together. And there are quieter problems behind it:

- every rerun pays for every email again, even the ones already read;
- a call that hangs holds an email for as long as the client is willing to wait.

This chapter makes Claimdesk dependable: it paces its calls so the limit is never hit, remembers what it has already
read, and has a plan for the calls that still fail.

:::mission
Pace model calls under a rate limit, and cache successful reads so a rerun costs nothing, without ever caching a
failure.
:::
:::

:::step{type=concept title="What can go wrong with one call"}
A model call is a network call to someone else's service. Each failure has its own cure:

| What happens | What it looks like | Cure |
|---|---|---|
| Too many requests | `RateLimitError` (HTTP 429) | send fewer: **pace** the calls |
| The service is slow or stuck | the call waits, then `APITimeoutError` | a **timeout**, then retry or give up |
| A short network or server problem | `APIConnectionError`, HTTP 500 to 503 | **retry** with backoff (chapter 6) |
| The same email read again | a second bill for the same answer | **cache** the answer |
| Nothing works for a while | every call fails | **fall back**: refer the claim to a person |

**Timeouts.** The OpenAI Python SDK waits up to **600 seconds** for an answer unless told otherwise (we checked the
version in the lab image: `read=600.0`). Ten minutes is far too long for one email. Chapter 9's `client()` already sets
`timeout=60`, and the SDK retries twice by itself (`max_retries=2`). That handles short hiccups; it does not help when
you are simply sending too fast.

**The fallback is already built.** When `safe_extract` cannot read an email, chapter 13's triage returns `refer`,
"could not read the email". The worst case is that a person does the job they do today. Never let a failed call lose
an email or invent a decision.
:::

:::step{type=concept title="Pacing: stay under the limit" file="18-reliability/reliable.py" line="16-30"}
Retrying after a 429 works, but it is like knocking on a door until someone opens: noisy, slow, and it uses up the
limit for everyone else on the same account. Better: never exceed the limit in the first place.

20 requests a minute means one every 3 seconds. A **pacer** remembers when the last call started and, before each new
call, sleeps for whatever is left of the gap:

```text
gap = 60 / per_minute                      20 a minute -> 3.0 s

call 1 at t=100.0    no previous call     -> go now, last = 100.0
call 2 at t=101.0    1.0 s since last     -> sleep 2.0, last = 103.0
call 3 at t=108.0    5.0 s since last     -> go now, last = 108.0
call 4 at t=108.0    0.0 s since last     -> sleep 3.0, last = 111.0
```

Note the last column: after sleeping, read the clock **again** and remember that time, the moment the call really starts.
Remember the time before sleeping and the next gap is measured from the wrong moment.

`Pacer` takes `clock` and `sleep` as arguments, with the real `time.monotonic` and `time.sleep` as defaults. The check
passes a fake clock instead, so it can test minutes of waiting in a millisecond. Taking time as a parameter is the
standard way to make time-based code testable.

`time.monotonic()` is used rather than `time.time()` because it never goes backwards, even if the computer's clock is
corrected while the batch runs.

`run_batch` uses `Pacer(19)`, a little under the limit, because the gateway counts per minute and a little margin is
cheaper than a failure.
:::

:::step{type=example title="Worked example: a pacer for a printer"}
This is only to read; it is not in your project. A shared office printer accepts at most 6 jobs a minute:

```python
class Spacer:
    def __init__(self, per_minute, clock, sleep):
        self.gap = 60 / per_minute           # 10 seconds
        self.clock, self.sleep = clock, sleep
        self.last = None

    def wait(self):
        now = self.clock()
        if self.last is not None and now - self.last < self.gap:
            self.sleep(self.gap - (now - self.last))
            now = self.clock()               # the moment the job really goes
        self.last = now
```

- `self.last is None` means no job yet: the first one never waits.
- `self.gap - (now - self.last)` is the part of the gap still to go.
- After sleeping, `now` is read again, so `last` is the time the job was really sent.
:::

:::step{type=task task=pacer title="Your turn: the pacer"}
In `Pacer.wait` in `reliable.py`:

1. `now = self.clock()`.
2. If `self.last` is not `None` and `now - self.last < self.gap`: sleep `self.gap - (now - self.last)`, then read the
   clock again.
3. `self.last = now`.

Press **Check**.
:::

:::step{type=concept title="A cache: never pay twice for the same answer" file="18-reliability/reliable.py" line="8-14"}
Batches get rerun: after a crash, after a fix to the triage rules, for a report. With temperature 0 and the same prompt,
reading the same email again gives the same answer (usually) and costs the same money (always). So remember answers:

```text
key = sha256(prompt version + "\n" + email text)

in the cache?  yes -> return it, no call
               no  -> call the model; on success, store it under key
```

Three details make the difference between a cache that helps and one that hurts:

1. **The key includes the prompt version.** When you change the prompt (chapter 15's version 2), the old answers no
   longer describe what the new prompt would say. `PROMPT_VERSION` is part of every key, so changing it makes every
   email look new. Forgetting this is the classic cache bug: you change the prompt, rerun the eval, and measure the old
   prompt again.
2. **The key is a hash.** `hashlib.sha256` turns any text into a fixed 64-character fingerprint. The email itself is not
   the key, so the cache file holds no email text (chapter 17).
3. **Failures are never stored.** A `RateLimitError` is about that minute, not that email. If you cached it, the email
   would fail forever. Only successful reads go in.

`cached_extract` returns `(fields, problem, called)`. `called` tells `run_batch` whether a model call happened, so it can
count what the run cost.

:::diagram{name="fde-cached-call"}
One email through cached_extract, the pacer and the fallback.
:::
:::

:::step{type=predict title="Guess first"}
:::question
You fix a typo in `SYSTEM` and rerun the batch, but forget to change `PROMPT_VERSION`. What happens?
:::
- [ ] Every email is read again with the new prompt
- [x] Every email comes from the cache: the new prompt is never used
- [ ] The cache is deleted
:::explain
The keys are the same as before, so every lookup hits. Your eval would report the old prompt's results under the new
prompt's name. Change the version with every prompt, schema or model change.
:::
:::

:::step{type=task task=cache title="Your turn: the cache"}
In `cached_extract`:

1. `key = cache_key(text, version)`.
2. If `key` is in `cache`, return `(cache[key], None, False)`.
3. Otherwise `fields, problem = extract(text)`. If `problem` is not `None`, return `(None, problem, True)` without storing.
4. Store `fields.model_dump()` under `key` and return `(cache[key], None, True)`.

Press **Check**.
:::

:::step{type=try title="The same 30 emails, through the gateway"}
With the real model:

```text
$ python reliable.py
first run: 30 model calls, 0 failed, 93 s []
second run: 0 model calls, 0 failed, 0 s []
```

Compare with chapter 9: the same 30 emails, the same limit, **15 failures then, none now**. Pacing at 19 a minute made the
batch take 93 seconds, about what the arithmetic says (29 gaps of 3.16 seconds, plus the last call). A slower batch that
finishes is worth more than a fast one that does half the job.

The second run read all 30 from `cache.json`: no calls, no cost, no time. That is what every rerun now costs, until the
prompt version changes.
:::

:::step{type=history title="Remembering the slow answer"}
:::before{title="Before: every read went to the slow memory"}
Early computers had a small amount of fast memory and a large amount of slow memory. Every time the processor needed a
value from the slow memory, it waited, even if it had used the same value a moment ago.
:::

In 1965 Maurice Wilkes, who led the team that built the EDSAC computer at Cambridge, published a short paper describing
a small, fast "slave memory" that keeps copies of recently used values, so a repeated read does not go to the slow memory
at all. In 1968 IBM announced the System/360 Model 85, the first commercial computer with such a memory, and called it a
**cache**.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-wilkes.webp" alt="Maurice Wilkes, an older man in glasses and a pinstriped suit, arms folded, standing in front of a pegboard wall with computer disks and a tape reel hung on it." credit="University of Cambridge Computer Laboratory Archive" license="CC BY 2.0 UK" source="https://commons.wikimedia.org/wiki/File:Maurice_Vincent_Wilkes_1980_(3).jpg"}
Maurice Wilkes at his retirement from the Cambridge Computer Laboratory, 1980.
:::

The same idea now sits everywhere: in processors, in web browsers, in front of databases, and in front of model calls.
And caches still have the problem Wilkes's design had to handle: knowing when a remembered answer is no longer true.
That is what `PROMPT_VERSION` is for.

:::solved
Keep the answer to a slow, expensive question, and give it again when the same question comes back, until something
makes it stale.
:::

:::timeline
- **1949** EDSAC runs its first program at Cambridge.
- **1965** Wilkes describes "slave memories".
- **1968** IBM announces the System/360 Model 85, with a cache.
- **Today** Model providers offer their own caches for repeated prompt text.
:::

:::funfact
Wilkes received the Turing Award in 1967, the second person ever to receive it.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why is a failed read never stored in the cache?
:::
- [ ] Failures take too much space
- [x] A rate limit or timeout is about that moment, not that email; storing it would make the email fail forever
- [ ] JSON cannot store errors
:::explain
Only answers belong in a cache. Problems are tried again next time.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Pacing at 19 a minute makes 30 emails take about 93 seconds. Why is that better than sending them all at once?
:::
- [ ] It is not; faster is always better
- [x] All 30 are read, instead of half failing and needing another run
- [ ] The model gives better answers when it is slower
:::explain
Chapter 9's fast batch lost 15 emails. A predictable 93 seconds beats an unpredictable half.
:::
:::

:::step{type=deep-dive title="Go deeper: reliability in production"}
**Many workers, one limit.** A pacer in one process does not know about another. With several workers, share the
limit through something they all see, like Redis (LabBox's own gateway counts requests per minute this way).

**Retry with jitter.** When retries are needed, add a little randomness to the waits, so many clients that failed
together do not all retry at the same instant (chapter 6).

**A second model.** Some teams fall back to another model or provider when the first is down. It must pass the same
evals (chapter 15) first, or the fallback quietly lowers quality.

**Queues.** At larger scale, claim emails go into a queue and workers take them at the rate the limit allows. Nothing is
lost if Claimdesk restarts; the queue still holds the emails.

**Cache lifetime.** Cached answers hold customer data in derived form. Give the cache file the same access rules and
retention as the logs (chapter 17).
:::

:::step{type=recap}
You can now:

- name what goes wrong with a model call and the cure for each: pacing, timeouts, retries, caching, falling back to a
  person;
- write a pacer that keeps calls under a rate limit, with time passed in so it can be tested;
- cache answers under a hash of the prompt version and the text, and never cache a failure;
- show the result on the real batch: 30 calls, none failed, and a rerun that costs nothing.

Next, chapter 19: before adjusters rely on Claimdesk's drafts, run it in shadow mode beside them for a week and compare.

:::photo{src="/lesson-images/forward-deployed-engineer/fde-18-notes.webp" alt="Handwritten notes about reliability: Pace calls to stay under the limit. Read the clock again after sleeping. Cache by prompt version and text. Never cache a failure. 30 calls, none failed, 93 seconds. When all else fails, a person decides." ai="true"}
One page of notes for this chapter.
:::
:::
