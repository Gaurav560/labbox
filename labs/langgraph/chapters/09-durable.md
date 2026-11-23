:::step{type=story title="The SMS gateway went down at night"}
A repair job at the water board has three steps: **book a crew**, **order the parts** (a 200 mm valve and two couplings,
Rs 18,000), and **send the citizen an SMS** with the time. The first two cost money. The third depends on a
government SMS gateway that times out a few times a week.

One night the gateway is down. The job books the crew, orders the parts, and crashes at the SMS. In the morning someone
runs it again, and a program that starts from the beginning books a **second crew** and orders the parts **again**. That
is Rs 18,000 of parts nobody needed, and two crews at the same street.

A job must be **durable**: a failure stops it, and running it again continues from where it stopped. Short failures
should not even stop it: a timeout deserves a second try. LangGraph gives you both, because a graph with a checkpointer
already saves every finished step.

:::mission
Give the SMS step a retry policy, then make `run_job` continue a stopped job instead of starting over, so that no crew
or part is ever booked twice.
:::
:::

:::step{type=history title="Transactions, logs and durable execution"}
:::before{title="Half-done work"}
A program that changes several things and crashes in the middle leaves the world half-changed: money taken from one
account and never added to the other.
:::

In **1981** Jim Gray's paper **"The Transaction Concept"** set out how databases make a group of changes all-or-nothing
and permanent once done, and how they recover after a crash. Databases do it with a **write-ahead log**: write down
what you are about to do, do it, and after a crash read the log to see what finished (IBM's **ARIES**, **1992**, is the
method most databases still follow). Workflows that run for minutes or days got the same treatment later: Uber built
**Cadence** (**2017**), and its authors went on to found **Temporal** (**2019**), naming the idea **durable execution**.
A LangGraph checkpointer is that log for your graph: every finished step is written down before the next one starts.

:::solved
**Crash, then continue.** A stopped run is a saved state plus "the next step is X", and running it again does only X
and what follows.
:::

:::timeline
- **1981** "The Transaction Concept" (Jim Gray).
- **1992** ARIES: recovery from a write-ahead log.
- **2017** Cadence at Uber; **2019** Temporal.
- **2024** LangGraph: checkpoints after every step.
:::
:::

:::step{type=concept title="Retry policies: try a flaky step again" file="09-durable/job.py" line="31-42"}
A node can carry a **retry policy**:

```python
graph.add_node("notify_citizen", notify_citizen,
               retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.5, retry_on=SmsTimeout))
```

| Setting | Here | Meaning |
|---|---|---|
| `max_attempts` | 3 | three attempts in all (the first one and two retries) |
| `initial_interval` | 0.5 | wait half a second before the first retry |
| `backoff_factor` | 2 (default) | then wait twice as long before each later one: 0.5 s, 1 s |
| `retry_on` | `SmsTimeout` | retry only this error; a bug in your code fails at once |

Only the failing node is retried, not the graph: the crew booked in the step before stays booked.
:::

:::step{type=task task=retry_sms title="Your turn: try the SMS again" file="09-durable/job.py" line="35-37"}
Give `notify_citizen` `retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.5, retry_on=SmsTimeout)` in
`add_node`, and remove the TODO.

Press **Check**.
:::

:::step{type=concept title="Continue, do not start over" file="09-durable/job.py" line="45-50"}
When a node fails for good, `invoke` raises the error, but the checkpointer has already saved every step that finished.
The thread's state says where it stopped:

```python
app.get_state(config).next      # ('notify_citizen',): the step it was about to run
app.invoke(None, config)        # no new input: continue the saved run from that step
```

Passing a **new input** with the same `thread_id` would start a fresh run from START (the old state is kept, and your
input is applied to it), which is exactly how the second crew gets booked. Passing `None` means "carry on".

How often the checkpoint is written is your choice too: `invoke(..., durability="sync")` saves before each next step
starts (safest), `"async"` saves while the next step runs (the default, faster), and `"exit"` only when the run ends
(fastest, but a crash loses the run).

:::diagram{name="lg-durable"}
A crash keeps everything up to the last finished step; `invoke(None, config)` runs only what is left.
:::
:::

:::step{type=task task=resume_job title="Your turn: continue, do not start over" file="09-durable/job.py" line="45-50"}
Finish `run_job(app, job)`: if `app.get_state(config).next` is not empty, return `app.invoke(None, config)`; otherwise
start the job with `app.invoke({"job": job}, config)`.

```bash run
cd /workspace/09-durable && SMS_FAILS=9 python main.py J-102
```

```bash run
cd /workspace/09-durable && python main.py J-102 && cat board_record.txt
```

Press **Check**.
:::

:::step{type=try title="Two timeouts, a crash, and a double order"}
With the retry policy and `run_job` finished:

```text
$ SMS_FAILS=2 python main.py J-101
J-101: starting
  SMS attempt 1
  SMS attempt 2
  SMS attempt 3
done:
  J-101: crew booked (South zone, tomorrow 8:00)
  J-101: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  J-101: SMS sent to the citizen
$ SMS_FAILS=9 python main.py J-102
J-102: starting
  SMS attempt 1
  SMS attempt 2
  SMS attempt 3
crashed: SmsTimeout: the SMS gateway did not answer in 10 seconds
saved: next step is ('notify_citizen',)
$ python main.py J-102
J-102: continuing at notify_citizen
  SMS attempt 1
done:
  J-102: crew booked (South zone, tomorrow 8:00)
  J-102: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  J-102: SMS sent to the citizen
```

J-101 met two timeouts and never noticed: the third attempt worked. J-102 met a gateway that stayed down: three attempts,
then the run crashed, with the crew and the parts saved and `notify_citizen` as the next step. The second run sent only
the SMS. The record file has one crew and one parts order for each job.

Here is the same crash with the unfinished `run_job` (it always passes a new input):

```text
$ SMS_FAILS=9 python main.py J-103
...
crashed: SmsTimeout: the SMS gateway did not answer in 10 seconds
saved: next step is ('notify_citizen',)
$ python main.py J-103
J-103: continuing at notify_citizen
  SMS attempt 1
done:
  J-103: crew booked (South zone, tomorrow 8:00)
  J-103: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  J-103: crew booked (South zone, tomorrow 8:00)
  J-103: parts ordered, Rs 18,000 (200 mm valve, 2 couplings)
  J-103: SMS sent to the citizen
```

(The first run is shortened with "...".) `main.py` read the saved state and printed "continuing at notify_citizen",
but `run_job` ignored it and started from START: a second crew and a second Rs 18,000 order. The checkpoint was there all
along; durability depends on the code that resumes.
:::

:::step{type=predict title="Guess first"}
:::question
`order_parts` itself fails after the parts were ordered but before it returned (a network error while reading the
supplier's answer). The job is resumed. What happens?
:::
- [ ] Nothing is ordered again: LangGraph knows the order went through
- [x] `order_parts` runs again, and may order twice: a step is saved only when it finishes
- [ ] The job skips to the SMS
:::explain
Checkpoints are saved between steps. Inside a step, protect money with an idempotency key (the supplier ignores a
second order with the same job id), or split the step.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `app.invoke(None, config)` do on a thread that stopped at `notify_citizen`?
:::
- [x] Continues the saved run from `notify_citizen`
- [ ] Starts the graph from START with an empty state
- [ ] Nothing, because the input is None
:::explain
No new input means "carry on from the saved state and its next step".
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why `retry_on=SmsTimeout` instead of retrying every error?
:::
- [ ] It is faster
- [x] A timeout may pass; a bug in your code will fail the same way every time, and retrying only delays the error
- [ ] Other errors cannot be retried
:::explain
Retry what is temporary (timeouts, rate limits); fail fast on everything else.
:::
:::

:::step{type=deep-dive title="Go deeper: durable jobs in production"}
**One side effect per node.** If a node books a crew and orders parts, a retry of that node does both again. Small
nodes, one side effect each, make retries and resumes safe.

**Idempotency keys.** Send the job id with every external call, and let the other system ignore repeats. Combined with
checkpoints, a resumed or retried step can never double an order.

**Who resumes?** Something must notice stopped threads and resume them: a nightly script, a queue, or LangGraph's own
server (chapter 21), which keeps runs and retries for you.
:::

:::step{type=recap}
You can now:

- explain durable execution: save each finished step, continue from the last one;
- retry a flaky node with a `RetryPolicy` limited to the errors that may pass;
- continue a stopped run with `invoke(None, config)` instead of starting over;
- spot where a resume can still repeat work, and protect it with small nodes and idempotency keys.

Next, chapter 10: interrupts, so a run can wait for a person's decision.

:::photo{src="/lesson-images/langgraph/lg-09-notes.webp" alt="Handwritten notes about durable execution: finished steps are saved; retry only what may pass; 3 attempts: 0.5 s, then 1 s; invoke(None, config) = continue; never book the crew twice" ai="true"}
One page of notes for this chapter.
:::
:::
