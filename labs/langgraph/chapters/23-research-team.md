:::step{type=story title="Why did Station Road get worse?"}
Leak complaints on Station Road tripled in 2025: 36 by the end of September, against 11 in the same months of 2024. The
executive engineer wants a short report before the monsoon: why, and what to do. The answer is somewhere in the board's
records: the pipe register, the complaint figures, the pressure log, the city's roadworks notes, rainfall, the crews'
field notes, the council's minutes. Seven documents, and no single one says "this is the cause".

This is a job for a team, built from what you already know: a **planner** that splits the topic into questions
(structured output, chapter 4), one **researcher** per question working in parallel (`Send`, chapter 6), each an agent
with tools to read the sources (chapter 13), a **writer** that turns the findings into a report, and a **review** that
checks every paragraph's citations in Python and sends the draft back if needed (`Command`, chapters 6 and 14).

:::mission
Fan out one researcher per question, and write the Python check that every paragraph of the report cites a source that
really exists.
:::
:::

:::step{type=history title="Reporters, editors and systematic reviews"}
:::before{title="One person reads everything"}
A single analyst reading every record in order is slow, and tends to stop at the first explanation that fits.
:::

Newsrooms have long split big stories: an editor assigns questions to reporters, each finds sources, and the editor
puts the story together and checks every claim. Medicine made the method strict: the **Cochrane Collaboration**
(**1993**) publishes **systematic reviews** in which every conclusion is traced to the studies behind it. Research agents
followed: Stanford's **STORM** (**2024**) wrote encyclopaedia-style articles by asking questions from several angles and
citing what it found, and OpenAI's **Deep Research** (**February 2025**) made multi-step, cited research a product.

:::solved
**Many sources read in parallel, one report, every claim traceable** to a named record.
:::

:::timeline
- **1993** Cochrane: systematic reviews.
- **2024** STORM: research by questions, with citations.
- **2025** Deep Research.
:::
:::

:::step{type=concept title="Plan, then one researcher per question" file="23-research-team/team.py" line="69-84"}
```python
def plan(state):           # structured output: Plan(questions=[...]), with the list of sources in the prompt
def fan_out(state):        # one Send("research", {"question": q}) per question
def research(task):        # a create_agent with list_sources and read_source; response_format=Finding
```

Each researcher is an agent that returns a `Finding` (the question, a short answer, and the sources it used) through
`response_format`, so the writer gets structured notes, not chat. `findings` has an `operator.add` reducer, so the
parallel results are collected into one list (chapter 6). The rate limiter keeps the parallel researchers under the
gateway's limit.
:::

:::step{type=task task=fan_out_questions title="Your turn: one researcher per question" file="23-research-team/team.py" line="74-77"}
Finish `fan_out(state)`: return `[Send("research", {"question": q}) for q in state["questions"]]`.

Press **Check**.
:::

:::step{type=concept title="Checking citations in Python" file="23-research-team/team.py" line="94-103"}
The writer is told to end every paragraph with its sources in square brackets. The first version of the check looked for
`[one-name]`, and on the first real run it rejected **every** paragraph:

```text
  review: ['no source: **Report on Leak Complaints and Maintenance Activities on St', 'no source: Over the past five years, there has been a notable increase ', ...]
```

The writer had cited, but as a list, `[complaints-2025, council-minutes, field-notes]`, and the report's title was
counted as a paragraph. The check now reads both forms with one pattern (`CITE`), and skips titles:

| Paragraph | Problem |
|---|---|
| `... raised in April [pressure-log].` | none |
| `... near the towers [field-notes, pressure-log].` | none |
| `The pipe is old.` | `no source: The pipe is old.` |
| `... said yes [council-notes].` | `unknown source [council-notes]`: no such record |
| `**Leaks on Station Road**` | none: a title |

A check like this is cheap, exact and never tired. It cannot tell whether the reasoning in a paragraph is right, only
whether its sources exist.

:::diagram{name="lg-research"}
Questions fan out to researchers in parallel; the findings come back together for the writer and the review.
:::
:::

:::step{type=task task=check_citations title="Your turn: check every paragraph" file="23-research-team/team.py" line="94-103"}
In `check_citations`, after `cited` is found: if it is empty, append `f"no source: {paragraph[:60]}"`; then append
`f"unknown source [{name}]"` for every name in `cited` that is not in `known`.

```bash run
cd /workspace/23-research-team && python main.py
```

Press **Check**.
:::

:::step{type=try title="Seven researchers, a clean review, and a missed connection"}
The first real run planned four questions, none about what changed in how the main was **operated**. Nobody read the
pressure log, and the report blamed normal rainfall and the roadworks. The planner now sees the list of records, and is
asked to cover every one that could explain the topic:

```text
$ python main.py
> Why have leak complaints on Station Road tripled in 2025, and what should the board do before the monsoon?
  plan:
    - What specific leak complaints have been recorded for Station Road in 2025 according to the complaints-2025 record?
    - What discussions or decisions regarding Station Road leaks are documented in the council-minutes?
    - What observations or issues related to the water pipes on Station Road are noted in the field-notes?
    - What is the condition and maintenance history of the pipes on Station Road as per the pipe-register?
    - What pressure readings have been recorded for the pipes on Station Road in the pressure-log?
    - What rainfall data is available for the area that could correlate with the increase in leak complaints?
    - Are there any ongoing or planned roadworks on Station Road that could affect the water supply or contribute to leaks?
  research: What is the condition and maintenance history of the pipes on Station Road as per the pipe-register?
    -> The pipes on Station Road are made of cast iron, with a diameter of 150 mm, and were laid in 1978. The last major maintenance work was conducted in 1996, which involved resealing the joints.  ['pipe-register']
  ...
  research: What pressure readings have been recorded for the pipes on Station Road in the pressure-log?
    -> On 14 April 2025, the supply pressure in the Station Road zone was raised from 2.1 to 3.0 bar to ensure water reaches the upper floors of Sunrise Towers, which has 14 floors.  ['pressure-log']
  research: What observations or issues related to the water pipes on Station Road are noted in the field-notes?
    -> The field notes indicate that 31 leaks were repaired on Station Road, with 22 of these occurring at pipe joints in the last 400 meters near Sunrise Towers, where pressure is highest at night. Additionally, 3 leaks were noted near the 300-meter mark, with the remaining leaks spread along the road.  ['field-notes']
  ...
  write: draft 1
  review: every paragraph cites a real source

...
Field observations reveal that 31 leaks have been repaired, predominantly at pipe joints in the last 400 meters near Sunrise Towers, where pressure is highest at night. The pipes, made of cast iron and laid in 1978, have not undergone major maintenance since 1996, raising concerns about their condition. The pressure readings indicate that the supply pressure was raised from 2.1 to 3.0 bar in April 2025 to ensure adequate water delivery to upper floors, which may have contributed to the increased leak incidents [field-notes, pipe-register, pressure-log].

Additionally, rainfall data shows that Ujjwal Nagar experienced 102% of the long-term average rainfall in 2025, which may correlate with the spike in leak complaints. Ongoing roadworks on Station Road, which involved exposing a water main, have also been noted, although no damage was reported during these activities. The combination of increased rainfall and ongoing construction may be exacerbating the existing issues with the water supply infrastructure [rainfall, roadworks, complaints-2025].

**Recommendation:** It is recommended that the council prioritize the replacement of the Station Road main pipeline in the 2026 budget to mitigate the ongoing leak issues. Additionally, the interim installation of the pressure-reducing valve should be approved to manage pressure-related leaks effectively while the main replacement is planned. Regular maintenance checks should also be instituted to prevent further deterioration of the existing infrastructure [council-minutes].
```

(Shortened with "..." where four findings and the first two paragraphs were.) Seven questions, seven researchers in
parallel, one draft, and a clean review. The report now has the real story: pressure raised in April, leaks at the joints
near the towers where pressure is highest, and a pressure-reducing valve as the fix before the monsoon.

Read it once more as the engineer. The pipe register says the main's **design pressure is 2.5 bar**; it was raised to
3.0 in April, and the complaints jumped from 5 in the first quarter to 14 in the second. That is the strongest evidence
in the records, and no paragraph says it: the pipe-register researcher summarised the pipe without the design pressure,
and the pressure-log researcher never saw the register. The report also still offers rainfall at **102% of normal** as a
possible cause, and calls March's finished roadworks "ongoing". Every sentence is cited; not every conclusion follows.
Splitting research makes it fast and broad, and loses the connections between documents. The writer needs the key facts
themselves, not only summaries, and a person still reads the reasoning.
:::

:::step{type=predict title="Guess first"}
:::question
The writer cites a record that does not exist, `[budget-2025]`, in two drafts in a row. What does the graph do?
:::
- [ ] Rewrites until it is fixed
- [x] Sends draft 1 back with the problem, then ends after draft 2 with the problem recorded in `problems`
- [ ] Deletes the paragraph
:::explain
`review` allows two drafts. After that the problems are kept in the state, for a person to see.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
Why does each researcher return a `Finding` instead of free text?
:::
- [x] The writer gets the answer and its sources as fields, ready to cite
- [ ] Free text is not allowed in a Send
- [ ] It is cheaper
:::explain
Structured findings keep the sources attached to each fact all the way to the report.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What can the citation check not catch?
:::
- [ ] A missing citation
- [ ] An invented source name
- [x] A wrong conclusion drawn from a real source
:::explain
The rainfall paragraph cites the right record and still draws the wrong conclusion from it.
:::
:::

:::step{type=deep-dive title="Go deeper: research agents"}
**Give the writer evidence, not summaries.** Let researchers return short quotes with their findings, so the facts that
connect documents (2.5 bar and 3.0 bar) reach the writer.

**A second round.** After the first findings, a node can ask "what is still unexplained?" and send new questions, the
way STORM asks follow-up questions.

**Cost.** Seven researchers, each reading several documents, is many calls. Count them; a background run on the server
(chapter 21) keeps a long study from blocking anyone.
:::

:::step{type=recap}
You can now:

- build a research team from a planner, parallel researchers, a writer and a review;
- return structured findings from agents with `response_format`;
- check citations in Python, in the format the model really uses;
- tell a well-cited report from a well-reasoned one.

Next, chapter 24: the capstone, Harsh complete.

:::photo{src="/lesson-images/langgraph/lg-23-notes.webp" alt="Handwritten notes about a research team: plan, fan out, write, review; Finding = answer + sources; citations checked in Python; cited is not the same as right; pass key facts, not summaries" ai="true"}
One page of notes for this chapter.
:::
:::
