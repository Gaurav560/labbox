:::step{type=story title="A plan for the monsoon"}
Every May the board must decide which streets get work before the rains: which mains to replace, which tanks to clean,
which crew goes where, and in what order. The facts are in three files: a year of complaints (149 rows), the pipe
register and the crew list. Writing the plan means reading, counting, comparing, and writing a document: a long task
with many steps, not one question and one answer.

The agents of Part 3 hold everything in one conversation, which fills up fast on a task like this. **Deep Agents**, a
library built on LangGraph, adds what long tasks need: **files** the agent reads and writes instead of keeping
everything in its messages, **subagents** it hands a piece of work to (each with a fresh, small context), and
**permissions** on what it may touch. `create_deep_agent` returns an ordinary compiled LangGraph graph.

:::mission
Build the planner as a deep agent that works on the real files in `data/`, give it a data-analyst subagent with an
exact counting tool, and read the plan it writes, number by number.
:::
:::

:::step{type=history title="Agents that work like engineers"}
:::before{title="One long conversation"}
Early agents kept every file they read and every result they got in one growing list of messages, until the important
parts were lost in the middle or the context ran out.
:::

Unix (**1970s**) made the file the common interface between small programs, each doing one job well. Coding agents
took the same road: in **2025** OpenAI's Deep Research and Anthropic's Claude Code showed agents that plan, keep notes in
files, and hand sub-tasks to helper agents. Later in **2025** LangChain released **Deep Agents**, a LangGraph library that
packages those patterns: a filesystem, subagents, long prompts with care built in, and middleware for summarising long
runs.

:::solved
**Long tasks in small pieces.** Notes go into files, sub-tasks go to helpers with their own context, and the main agent
keeps only what it needs.
:::

:::timeline
- **1970s** Unix: small programs, files between them.
- **2025** Deep Research and Claude Code.
- **2025** Deep Agents for LangGraph.
:::
:::

:::step{type=concept title="A deep agent, its files and its limits" file="22-deep-agents/planner.py" line="10-34"}
```python
create_deep_agent(model=model(), system_prompt=PLANNER, subagents=[ANALYST], permissions=NO_RAW_DATA,
                  backend=FilesystemBackend(root_dir="data", virtual_mode=True))
```

| Part | Here | What it gives the agent |
|---|---|---|
| tools it always has | `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `task` | files and delegation |
| `backend` | the real folder `data/`, seen as `/` | `/plan.md` is `data/plan.md`; `virtual_mode` keeps it inside |
| `permissions` | no reading `/complaints_2025.csv` | the planner must ask the analyst for numbers |
| `subagents` | `data-analyst` | the `task` tool can hand work to it |

The permission is a design decision. The planner could read 149 rows and count them by eye; models are poor at that, and
the rows would sit in its context for every later call. Forbidding the read forces the right path: ask the analyst, who
counts with Python.

Each model call also carries the descriptions of every tool (about 2,500 tokens here), so a deep agent run costs more
than a simple agent. The model here has a shared **rate limiter** (`InMemoryRateLimiter`, 0.3 calls a second), so a
long run stays under the gateway's 20 calls a minute instead of failing halfway.
:::

:::step{type=task task=deep_agent title="Your turn: a planner with files and a helper" file="22-deep-agents/planner.py" line="31-34"}
In `build_agent`, also pass `subagents=[ANALYST]` and `backend=FilesystemBackend(root_dir=root, virtual_mode=True)`.

The usual slip: leaving out `virtual_mode=True`. We tried the backend both ways on 26 November. With it, `/pipes.csv`
is `data/pipes.csv`, and `/etc/hostname` is "not found". Without it, `/pipes.csv` is "not found" (it means the real
`/pipes.csv`), and `/etc/hostname` could be read: the agent's files are no longer kept inside its folder.

Press **Check**.
:::

:::step{type=concept title="A subagent is a dict" file="22-deep-agents/planner.py" line="15-20"}
```python
ANALYST = {
    "name": "data-analyst",
    "description": "Answers questions about complaints_2025.csv with exact counts by street, kind and month.",
    "system_prompt": "You answer questions about the board's complaints with the count_complaints tool. ...",
    "tools": [count_complaints],
}
```

The planner sees the `description` in the `task` tool, and calls `task(description="...", subagent_type="data-analyst")`.
The analyst then runs as its own agent, with a fresh context, its own prompt and tools, and returns only its final
answer. `count_complaints` (in `analysis.py`) reads the CSV with Python's `csv` module, so its numbers are exact.

:::diagram{name="lg-deep-agent"}
The real run of 26 November, and a check of four of its numbers.
:::
:::

:::step{type=task task=analyst_subagent title="Your turn: the analyst's tool" file="22-deep-agents/planner.py" line="15-20"}
Give `ANALYST` its tool: `"tools": [count_complaints]`.

Without it, the analyst has no way to count exactly: its only source would be its own guesses. Keep the exact tool
with the agent whose job is the numbers.

```bash run
cd /workspace/22-deep-agents && python main.py
```

Press **Check**.
:::

:::step{type=try title="Exact counts, wrong arithmetic"}
```text
$ python main.py
> Prepare the monsoon readiness plan for 2026.
  [planner] read_file({'file_path': '/pipes.csv'})
  [planner] read_file({'file_path': '/crews.md'})
  [planner] task({'description': 'Analyze the complaints data for 2025 to identify the number of comp...', 'subagent_type': 'data-analyst'})
  [analyst] count_complaints({'street': 'Station Road'})
  [analyst] count_complaints({'street': 'Gandhi Chowk'})
  ... (one count for each of the eight streets)
  [planner] write_file({'file_path': '/plan.md', 'content': '# Ujjwal Nagar Water Board Monsoon Readiness Plan 2026\n\n## Streets ...'})

# Ujjwal Nagar Water Board Monsoon Readiness Plan 2026

## Streets Needing Work Before June

1. **Station Road**  
   - **Total Complaints:** 49 (41 leaks, 8 no water)  
   - **Pipe Age:** 48 years (laid in 1978)  
   - **Crew:** South crew 1  
   - **Action:** Main replacement (20 crew days for 1.2 km)

2. **Tilak Nagar**  
   - **Total Complaints:** 26 (22 no water, 4 dirty water)  
   - **Pipe Age:** 12 years (laid in 2011)  
   - **Crew:** East crew 2  
   - **Action:** Cleaning and maintenance (4 crew days)

3. **Gandhi Chowk**  
   - **Total Complaints:** 26 (22 dirty water, 4 leaks)  
   - **Pipe Age:** 38 years (laid in 1985)  
   - **Crew:** North crew  
   - **Action:** Cleaning tank and inlet (4 crew days)

4. **Old Market**  
   - **Total Complaints:** 21 (15 dirty water, 6 billing)  
   - **Pipe Age:** 51 years (laid in 1972)  
   - **Crew:** North crew  
   - **Action:** Main replacement (20 crew days for 0.8 km)
...
This plan prioritizes streets with the highest complaints and oldest pipes to ensure readiness for the monsoon.
```

(This is the run of 26 November, shortened with "...". The first run, when we wrote the chapter, sent the analyst one
count for the whole year instead of eight; the complaint numbers and the same three wrong pipe ages were in it too.)

The structure worked: the planner read the two small files, sent one task to the analyst, the analyst counted street
by street, and the plan landed in `data/plan.md`. The gateway's log shows what that costs: each of the planner's calls
carried between 1,835 and 3,258 tokens in, most of it the tool descriptions and the files read so far.

Now check the numbers, because the engineer will. **Every complaint count is right**: 41 leaks and 8 no-water on Station
Road, 22 dirty-water at Gandhi Chowk; they came from Python. **Every number the planner worked out itself is wrong**:

- Pipe ages: Station Road (1978) is 48 in 2026, correct; but 1985 is 41, not 38; 1972 is 54, not 51; 2011 is 15, not 12.
  The same three mistakes appeared in both runs.
- Crew days: the crew list says 20 days per kilometre, so 1.2 km takes 24, not 20, and 0.8 km takes 16, not 20.
- "Cleaning and maintenance (4 crew days)" for Tilak Nagar: 4 days is the crew list's figure for **a tank and its
  inlet**, and Tilak Nagar has no tank. (Gandhi Chowk's tank cleaning is right.)

It also says it put the "oldest pipes" first; Old Market's 1972 cast iron is older than Station Road's and comes last. The lesson of this chapter is the
analyst's: give the agent tools for everything that must be exact (dates, sums, rates), not only for counting, and have
a person read the plan before it is used. Delegation made the counts right; it did nothing for the arithmetic it kept.
:::

:::step{type=predict title="Guess first"}
:::question
You remove the permission, so the planner may read `/complaints_2025.csv`. What is the most likely change?
:::
- [x] Maybe nothing you can see: its prompt also says to ask the analyst; but that is now a request, not a rule
- [ ] It must read all 149 rows
- [ ] The analyst stops working
:::explain
We tried it on 26 November: without the permission, the planner still asked the analyst, because the system prompt
says "You may not read /complaints_2025.csv". A prompt is a request the model follows when it does; a permission is
enforced by the code every time. Keep both.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a subagent return to the planner?
:::
- [ ] Its whole conversation
- [x] Only its final answer; its tool calls stay in its own context
- [ ] A file
:::explain
That is the point of a subagent: the main agent's context stays small.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why does `virtual_mode=True` matter with `FilesystemBackend`?
:::
- [x] Paths stay inside the root folder, so the agent cannot read or write elsewhere on the machine
- [ ] It keeps files in memory
- [ ] It makes reading faster
:::explain
We tried it: without `virtual_mode`, the backend read `/etc/hostname`. An agent that writes files must not be able
to reach `/etc` or your home folder.
:::
:::

:::step{type=deep-dive title="Go deeper: Deep Agents in practice"}
**Planning tools.** `TodoListMiddleware` (from LangChain) adds a `write_todos` tool for agents that should keep a visible
plan; it costs another long tool description on every call.

**Other backends.** `StateBackend` keeps files in the graph's state (saved with each checkpoint), `StoreBackend` in a
LangGraph store (shared across threads), and `CompositeBackend` mounts several at different paths.

**Approvals.** `interrupt_on={"write_file": True}` pauses before every write for a person to approve, using chapter
10's `interrupt`.

**Budgets.** Watch the token use of long runs. A learner's daily budget here is 50,000 tokens across all labs; a deep
agent that reads big files can use a large part of it in one run.
:::

:::step{type=recap}
You can now:

- build a deep agent with files, a subagent and permissions;
- keep an agent's files on disk, inside one folder, with `FilesystemBackend`;
- give a subagent the exact tool its job needs;
- check an agent's document number by number, and tell delegated facts from improvised arithmetic.

Next, chapter 23: a research team, built from the parts of this course.

:::photo{src="/lesson-images/langgraph/lg-22-notes.webp" alt="Handwritten notes titled Deep Agents, files, helpers and permissions for long tasks: create_deep_agent gives an agent file tools, subagents it can hand work to, and permissions on what it may touch, and returns an ordinary LangGraph graph; read pipes and crews, task to the data-analyst, the analyst counts with Python, write /plan.md, a person checks it; complaint counts from Python were all right; pipe ages and crew days were wrong, twice; without virtual_mode it could read /etc; a prompt is a request, a permission is a rule" ai="true"}
One page of notes for this chapter.
:::
:::
