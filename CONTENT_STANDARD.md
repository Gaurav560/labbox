# The LabBox teaching standard

Every LabBox course should be good enough to stand next to the best learning platforms in the world,
while keeping learners calm, unhurried and confident. Depth is welcome; confusion is not. This page is
the checklist for every chapter.

## 0. The template: Spring Boot (owner, 21 November)

The owner, after the full rewrite: "this one is much better, save it as template for rest". **The Spring Boot
course (`labs/spring-boot-first-api`) is the template for every LabBox course from now on.** When in doubt,
open a Spring chapter and do what it does. Where this page and that course disagree, the course wins. Good
chapters to copy from: 0 (welcome and history), 1 (HTTP with a running API), 4 (start-up), 6 (dependency
injection), 21 (relationships and N+1), 29 (calling services), 30 (capstone).

What makes it the template, as a checklist for every new course:

1. **Self-sufficient.** A learner with zero knowledge needs nothing else: no videos, no search engine, no
   chatbot. Every term is explained where it first appears; every prerequisite gets its own chapter (Spring has
   "How the web works" and "Maven and the pom.xml" before any Spring code).
2. **A teacher's voice.** "You", "let's", the problem before the answer, why before how, every line of code read
   aloud, what the learner will see on screen, the mistakes beginners really make, and a recap of what they
   *can now do*.
3. **Full lessons, not notes.** No word limit. One idea per step, explained completely, in short paragraphs.
   A chapter takes 35 to 60 minutes.
4. **Parts and a running project.** Chapters are grouped in parts (Spring: foundations, REST APIs, data,
   production basics), numbered from 0 when there is an introduction, building one project (the Shop API).
   Each chapter's code lives in its own folder named like the chapter (`11-reading-the-request/`).
   The first chapter of each part names it in `lab.yaml` (`part: REST APIs`); the skill map draws every part as
   its own metro line.
5. **The code follows the lesson.** Every step about project code names its file and lines
   (`file="..." line="..."`); task steps open their own TODO; example code that is not in the project says so.
6. **Everything quoted is real.** Every log line, curl answer, error message, stack trace line and SQL statement
   in a lesson was captured by running the chapter's actual project in the lab image. Never invent output.
7. **See it, break it, fix it.** Each chapter makes the learner *see* the problem first (a `try` step with the
   real wrong output: a 404, a 500, six SQL queries, a receipt with someone else's tea), then fix it in a task,
   then see the right output. If the project has no way to see the problem, add one (a small endpoint, a fake
   service the learner runs in a second terminal).
8. **Watch it run.** Processes (start-up, a request's journey, a bean's life, a transaction) get a calm playing
   timeline (`SketchSteps`); state that changes step by step gets a trace table. Diagrams: hand-drawn outlines,
   plain fills, normal font.
9. **Two tasks per chapter, each a real skill**, with a check that runs the learner's code (or their own tests,
   against a planted bug) and failure messages that say what happened, why, and what to try. Starter TODOs say
   the goal, not the answer.
10. **Honest depth.** Each chapter ends with quick checks and a "Go deeper" step that connects to production
    (what real teams add, and why), so experienced learners are not bored and beginners know what comes next.

### The voice, by example (Spring Boot chapter 14, "Layers")

The checklist says *what*; this says *how it sounds*. Every excerpt is real; copy the shape, not the words.

**A story opens with a concrete pain in the running project**, told in short sentences that build, then says
why the idea matters for the learner's whole career:

> Picture the Shop API a year from now if every endpoint is written the quick way: the controller reads the
> request, looks up products in the database, applies the discount rules, calculates GST, checks stock, and
> builds the response, all in one method. It works. Then the same discount rule is needed by the mobile app's
> endpoint, the admin endpoint and the nightly report, so it gets copied three times. Then the rule changes,
> and one copy is forgotten.
>
> ... Once you see it, you will recognise it in every Spring project you ever open.

Then a one-line `:::mission`: *Move a calculation out of the controller into the service, and give the
repository a proper query method.*

**A concept names the thing, bolds the key terms, and states the rule plainly** (in bold, once). It links back
and forward ("chapter 5", "in Part 3") so the course feels like one story:

> The rule that makes it work: **each layer only calls the layer directly below it.** Controllers call
> services, services call repositories. A controller never reaches into a repository, and a repository never
> calls a service.

It also answers the doubt the learner is having: "Three classes instead of one looks like more work. Here is
what you get back:".

**A worked example shows before and after**, and the comments say what job each line does
(`// data access`, `// business rule: 1 point per Rs 100`).

**A try step points at the code on screen, names the flaw, runs it, and reads the real output aloud:**

> Look at `averagePrice()` in `ProductController`, on the right. It works, but it breaks the rule twice: ...
> It answers `3950`: the average of 2000, 3000, 1800 and 9000. The right number, from the wrong place.

**A task step is numbered, concrete actions** naming the file and method, offers a choice where there is one
("You can move the loop from the controller, or use `mapToInt(...)` with `average()` or `sum()`"), says what
stays true afterwards, and ends with "Press **Check**." Its title is "Your turn: ...".

**In `lab.yaml`** a task title is a short lowercase action (`move the average into ProductService`). The
three hints climb: what is wrong now ("ProductService.averagePrice() returns 0, and the controller does the
work itself."), where to work ("Move the loop from the controller into averagePrice() ..."), nearly the answer
("In the controller, just return what the service method gives; ..."). `examples` show the call and what it
gives, with a short note ("worked out by the service").

**A starter TODO states the goal, never the code:**

```java
// TODO (task thin_controller): this works, but the controller does the service's job and reads the
// repository itself. Move the calculation into ProductService.averagePrice() and call that here.
```

**A check fails in the order of the likely mistake**, with expected and actual values, and names the "right
answer, wrong place" case kindly; **a pass says why it matters**:

> ProductService.averagePrice() is right, but GET /products/average-price does not call it: the controller
> still does the work itself.
>
> The controller only translates HTTP; the rule lives in the service, where any other caller can reuse it
> and a test can check it.

**Quick checks are real decisions** ("Where does the rule 'orders over Rs 500 get free delivery' belong?"),
three options, and a one- or two-sentence explanation of why.

**The recap starts "You can now ..."**, lists skills (not topics) in bullets, and ends with the next chapter:
"Next, chapter 15: changing existing products properly, with PUT and PATCH."

**Everyday, consistent world.** Prices in Rs and paise, masala tea, samosa, GST, a nightly report: familiar,
never jargon, the same Shop API throughout. No hype words, almost never an exclamation mark (one in 31 chapters);
calm confidence.

### Curiosity first (owner, 22 November, for the language courses)

The owner, starting the Python rewrite: "always with curiosity, like teaching a child one on one. interesting,
animated, cool images, tasks and much more." On top of everything above:

- **Open with a question or a small surprise** the learner wants answered: "What happens when you press
  Enter?", "Can a computer get a sum wrong?" (`0.1 + 0.2`), "Is 2100 a leap year?". Then answer it.
- **Guess before you tell.** Ask the learner to predict, then run it, then explain: "Surprised? Here is what
  happened." Celebrate the "aha" without hype.
- **Animate what is invisible.** A playing timeline (`SketchSteps`) for every process the learner cannot see
  (how Python runs a file, one function call, reading a traceback), and a trace with Play for every loop.
- **One small running project, with a name** (Python from zero: **Pocket**, a money tracker): tasks feel like
  giving it new powers, not exercises.
- **Invite play.** "Now change `chai = 15.5` to `20` and run it again." The learner changes code and sees
  what happens long before the task.
- Still precise: curiosity lives in the questions and reveals, not in piling up analogies. Every output is
  still captured from the real lab image.

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
- **Length.** As long as the topic needs (owner: "if it requires 30 lessons, do it"). Spring Boot is 31
  chapters, 61 tasks, about 20 hours. Beginner language courses are 13 chapters or more.

## 2. The chapter

In this order (one idea per step, each a complete lesson; see the Spring chapters for the shape):

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
a new learner to grasp". Every new idea is **taught**, not announced. There is no word limit on a step
(owner, 21 November: "make every lesson an actual lesson"); a step is as long as the idea needs:

1. **Why it exists**: the problem this idea solves, in one or two sentences, before any syntax.
2. **What it is, technically**: a plain, precise definition and what happens at runtime (what the
   framework, the language or the machine actually does), shown with a diagram or a trace of the real
   mechanism when it is invisible. **Prefer plain technical explanation to analogy** (owner, 21
   November: "plain simple technical explanations will be too good to understand"); use an everyday
   comparison only rarely, where it genuinely makes a hard idea click.
3. **In code**: a small sample walked through slowly, saying what each part does and why.
4. **Careful**: the confusion beginners really have, named kindly, with how to spot it.
5. **Check yourself**: one line the learner can answer in their head before moving on.

Each step is a complete lesson on one idea: everything the learner needs to understand it, in plain
words and short paragraphs, never cut short to save space. Never assume a term is known; define it the
first time, in place.

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

**Photos and handwritten notes (owner, 22 November).** Real photos are welcome where they show something real
and interesting: the person who made the language, the thing a name comes from, a historic object (Python's
story shows Guido van Rossum, a ball python, and the 1947 logbook page with the moth). Only freely licensed
photos (Wikimedia Commons), saved in `frontend/public/lesson-images/<course>/` (WebP, about 1000 px wide),
with the credit shown under them: `:::photo{src="/lesson-images/..." alt="..." credit="..." license="..."
source="https://commons.wikimedia.org/..."}` and a one-line caption. Never an AI image of a real person.
Each chapter's recap may end with one AI-drawn page of **handwritten notes** (`ai="true"`): five or six short
lines of the chapter's key ideas, checked letter by letter before use (image models misspell and miscount
digits). Photos never go on task or quick-check steps; one per step, two on a history step. The validator
rejects unknown picture and diagram names, traces without a table, code in a picture that is not also in a
code block of its step, and photos without a file, alt text or credit.

## 4. Words

- Plain words. Explain every new term the first time it appears, right there, in one line.
- Short sentences and short paragraphs, so a long lesson still reads easily. There is no word limit:
  a step is a real lesson, as long as the idea needs, never squeezed to fit a number.
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
