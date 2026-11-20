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
2. **Picture it**: an everyday comparison (a list is a numbered shelf, a reference is an address on
   an envelope, a goroutine is a second cook in the kitchen).
3. **In code**: a small sample walked through slowly, saying what each part does and why.
4. **Careful**: the confusion beginners really have, named kindly, with how to spot it.
5. **Check yourself**: one line the learner can answer in their head before moving on.

More, smaller steps beat fewer, denser ones. Never assume a term is known; define it the first time,
in place.

### Pictures: small, consistent, always meaningful

Pictures help when they show something words alone cannot. One style everywhere, never decoration:

- **The task card** (every task): two or three `examples` in `lab.yaml` (`call`, `gives`, optional
  `note`) are drawn at the top of the task as "what your code should do". Use the same examples as
  the task text, short enough to read at a glance (90 characters at most).
- **Picture it** (`:::picture{name=...}`, `frontend/src/lesson/Pictures.tsx`): a small hand-drawn
  picture of the everyday comparison (a recipe card, a phone book, a notebook). At most one per step,
  with a one-line caption that says what to notice. One look, two moods: a sketch in light ink with a
  violet accent in the dark theme, notebook paper with blue pen and a yellow highlighter in the light
  theme. Everyday words are handwritten (Caveat); **code stays in the code font**, is listed in
  `pictures.json`, and must also appear in a code block of the same step (the validator checks it):
  learners never copy from a drawing.
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
