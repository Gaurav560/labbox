# The LabBox teaching standard

Every LabBox course should be good enough to stand next to the best learning platforms in the world,
while keeping learners calm, unhurried and confident. Depth is welcome; confusion is not. This page is
the checklist for every chapter. The pilot is Python from zero: chapter 1 ("The story of Python") and
chapter 6 (Lists).

## 1. The course

- **Style.** Beginner courses ("from zero") are plain, with everyday examples (marks, prices, names).
  Advanced courses start with a simple story that needs no special knowledge (no sports jargon, no
  business terms).
- **History, always.** Chapter 1 has a `history` step, "The story of X", with:
  - **Before X**: the world before it existed, what people used and why it hurt (`:::before`);
  - **the spark**: who built it, when, where;
  - **the problem it solved** (`:::solved`);
  - **a timeline** of 3 to 5 milestones (`:::timeline`, a list like `- **1991** First public release.`);
  - **who maintains it** today (company, foundation, community);
  - **where it is used**: industries and well-known users (`:::usedby{title="Industries"}`,
    `:::usedby{title="Used at"}`);
  - **a fun fact** (`:::funfact`), and something to try if it fits.

  Every fact must be accurate and checkable: no invented dates, people or users.
- **Length.** A full course is 10 to 13 chapters, about 25 tasks, 3 to 5 hours.

## 2. The chapter

In this order (each step short, one idea per step):

1. **Why** (`story`): two or three lines on why this matters, and the mission.
2. **Idea** (`concept`): one idea, in plain words, with a small code sample.
3. **Worked example** (`example`): the exact pattern the task needs, solved step by step on a
   *different* problem, with every line explained.
4. **Guess first** (`predict`): one question that makes the learner think before they type.
5. **Try it** (`try`): a command they run and see for themselves.
6. **Easy win** (`task`): the first task is a warm-up that uses the worked example's shape.
7. **Next idea** (`concept`), with a **picture** (`:::diagram{name=...}`) when the idea is invisible
   (memory, references, concurrency).
8. **Stretch task** (`task`): the real challenge of the chapter.
9. **Quick check** (two `predict` steps, "Quick check (1 of 2)"): recall, not trickery.
10. **Go deeper** (`deep-dive`): optional depth for experienced engineers.
11. **Recap** (`recap`): four lines to remember.

## 3. Explain, do not just state

The owner's verdict on the first Go course: "a little straight, just to the point, very difficult for
a new learner to grasp". Every new idea is **taught**, not announced, in small steps (each under the
validator's 120 words of prose; code does not count):

1. **Why it exists**: the problem this idea solves, in one or two sentences, before any syntax.
2. **What it is, technically**: a plain, precise definition and what happens at runtime (what the
   framework, the language or the machine actually does), shown with a diagram or a trace of the real
   mechanism when it is invisible. **Prefer plain technical explanation to analogy** (owner, 21
   November: "plain simple technical explanations will be too good to understand"); use an everyday
   comparison only rarely, where it genuinely makes a hard idea click.
3. **In code**: a small sample walked through slowly, saying what each part does and why.
4. **Careful**: the confusion beginners really have, named kindly, with how to spot it.
5. **Check yourself**: one line the learner can answer in their head before moving on.

More, smaller steps beat fewer, denser ones. Never assume a term is known; define it the first time,
in place.

**Talk to one learner (owner, 21 November):** "the users must have felt like I am talking to him or her
only, in an interactive way; not taking shortcuts and just finishing the stuff." Write as a teacher
sitting next to one person: "you" and "let's", start from where the last chapter left them, show the
problem before the answer, ask them to run, guess or look before you tell, and say what they will see
on screen. Never squeeze several ideas into one list or table to save space. The goal of a course: a
learner who starts with zero knowledge finishes able to build the thing alone, and confident.

**The lesson and the code stay in sync (owner, 21 November):** a step about a file in the project names
it, and reaching the step opens that file in the editor with those lines selected:

```text
:::step{type=concept title="What SpringApplication.run does" file="02-app-startup/src/main/java/com/shop/ShopApiApplication.java" line="10"}
```

`line` is one line or a range (`line="9-12"`). Task steps need nothing: they open their own task's
`TODO (task <id>)`. A step that shows code which is **not** in the project says so in its first lines
("only to read; it is not in your project"), so nobody hunts for it. The validator fails a `file` that
is not in `starter/` or a line past its end.

### Visuals: the owner's rules (20 November)

| Kind | Use | What it is for |
|---|---|---|
| Architecture diagrams | Definitely | API communication, databases, authentication, microservices, system architecture |
| Conceptual diagrams | Definitely | Functions, loops, memory, objects, inheritance, threads, asynchronous execution |
| Execution visualizations | **High priority** | How variables change, how functions run, how data moves; prefer interactive (`:::trace`) |
| Code examples | Essential | Real code in the lesson, highlighted and explained. Never turn code into an image |
| Decorative images | Sparingly | No generic AI illustrations, stock photos or images that teach nothing |

### Pictures: small, consistent, always meaningful

**Where pictures go (the validator enforces it).** A picture must carry an idea the words struggle with;
anything else is an extra thing to look at, and learning research (the coherence principle, and
"seductive details") shows extra pictures lower what people remember. So:

- One everyday picture per **idea**, on the **concept** step that teaches it (or a worked example
  when the idea is a mechanism, like two cooks working at once). Never three pictures of one idea.
- Technical diagrams may also sit on a **try it** step, to explain what the learner just ran.
- **Never** on task steps (the task, its card and the Check button must stay in view), recaps, quick
  checks, story steps or go-deeper steps. At most one picture or diagram per step.
- Prefer a **"watch it run" trace** on the worked example: seeing the program itself run teaches more
  than a picture of it.

Pictures help when they show something words alone cannot. One style everywhere, never decoration:

- **The task card** (every task): two or three `examples` in `lab.yaml` (`call`, `gives`, optional
  `note`) are drawn at the top of the task as "what your code should do". Use the same examples as
  the task text, short enough to read at a glance (90 characters at most).
- **Picture it** (`:::picture{name=...}`, `frontend/src/lesson/Pictures.tsx`) shows an everyday
  comparison. Use at most one picture or diagram per step, with a one-line caption that says what to
  notice. Both directives use inline SVG with shared theme colors. Keep the geometry and labels
  identical on warm off-white and charcoal backgrounds. Use printed Inter for headings and labels,
  monospace for code, and an outline or label wherever color distinguishes elements. Examples include
  `recipe-card` (functions), `labelled-jars` (variables and types), `fork-in-road` (decisions),
  `running-track` (loops), `beads-on-string` (text), `egg-box` (lists and arrays), `notebook-vs-form`
  (fixed versus growing), `phone-book` (maps), `guest-list` (sets), `blueprint-houses` (classes),
  `plug-socket` (interfaces), `fire-alarm` (exceptions), `result-and-note` (Go errors),
  `envelope-address` (pointers and references), `conveyor-belt` (streams), `file-lines` (files and
  CSV), `two-cooks` (concurrency), `library-shelves` (hash codes). A picture that shows code takes it
  from the chapter (`code='phones.get("Riya")'`), draws it in the code font, and the validator checks
  that the same code is in a code block of that step: learners never copy from a drawing.
- **Watch it run** (`:::trace{title='...'}` around a table): one row per moment of a program, one
  column per variable, and a `note` column in plain words. The learner steps through it and sees
  values change. Use it where beginners lose track: loops, a "best so far", a map filling up. Up to
  12 rows; titles with double quotes use single quotes around them.
- **Diagrams** (`:::diagram{name=...}`) stay for technical ideas you cannot see (references,
  memory, concurrency).

No photos or generated images in lessons: they are heavy, drift in style and fight the themes. The
validator rejects unknown picture and diagram names, traces without a table, and code in a picture
that is not also in a code block of its step.

## 4. Words

- Plain words. Explain every new term the first time it appears, right there, in one line.
- Short sentences. No walls of text: concepts stay under the word limit the validator checks.
- Never blame. Mistakes are normal: "If you guessed X, you are in good company."
- Code samples fit the lesson panel (about 50 characters a line): put long comments on their own line.

## 5. Checks

- **A failure says three things**: what happened (the exact call and result), why (the likely
  mistake), and what to try next. Recognise the common wrong answers and name them kindly.
- **A pass teaches too**: one line on what they got right and why it matters (not just "ok").
- Test the edges that real learners miss (empty input, the boundary value, extra spaces), and run
  every typical wrong answer before calling a chapter done.
- Hints climb a ladder: a nudge, then the tool to use, then nearly the answer (never a solution line;
  the validator refuses those).

## 6. Done means

- `scripts/labbox validate <lab> --strict` passes, and `scripts/labbox test-lab <lab>`: the starter
  fails every task and the solution passes every task.
- Every typical wrong answer was run and fails with its lesson.
- The chapter was read in the browser at the default text size, in the dark and light themes.
