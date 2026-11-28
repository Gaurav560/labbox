:::step{type=story title="What happens when you press Enter?"}
Here is a question most people never ask: when you tap an app on your phone, who is telling the phone what to
do?

Somebody wrote it down. Every app, every game, every website is a list of instructions that a person typed
into a plain text file. The computer reads that list and does exactly what it says: no more, no less, and
very, very fast.

In this course *you* write those lists, in a language called **Python**. By the end you will have built
**Pocket**, a small program that keeps track of where your money goes. Today Pocket learns to talk.

:::photo{src="/lesson-images/python/ball-python.webp" alt="A close-up of a ball python snake" credit="Holger Krisp" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Python-regius-kopf-k%C3%B6nigspython.jpg"}
Meet a python. The language you are about to learn has the same name, but it was not named after this snake. The story of Python, in the next step, tells you what it was named after.
:::

:::mission
Make Pocket say its first two sentences, then find and fix two mistakes in a program that refuses to run.
:::
:::

:::step{type=history title="The story of Python"}
Python is one of the most used programming languages in the world. It started as one person's holiday
project.

:::before{title="Before Python"}
In the late 1980s, programmers mostly chose between two kinds of tools. **C** is a language that runs very
fast, but you write long, careful code and manage the computer's memory by hand, so one small memory mistake
can crash the whole program. **Shell scripts** are short lists of terminal commands saved in a file: quick to
write, but they turn messy beyond a few lines. Guido van Rossum, a programmer at the CWI research institute in Amsterdam, kept hitting jobs that
were too awkward for a shell script and too slow to write in C.
:::

:::solved
A language that is as **quick to write** as a script, **powerful enough** for real programs, and above all
**easy to read**. Python code is read far more often than it is written, so it looks almost like plain
English, and its indentation is part of the language.
:::

:::timeline
- **1989** Guido starts Python as a hobby project over the Christmas holidays.
- **1991** The first public release, version 0.9.0.
- **2000** Python 2.0 adds list comprehensions (a short way to build a list, chapter 11) and better automatic
  clean-up of memory the program no longer uses.
- **2008** Python 3.0 cleans up old design mistakes, on purpose breaking some old code, which needed changes
  to run on it.
- **2020** Python 2 reaches its end of life on 1 January: no more fixes, not even for security problems. Python
  3 is the Python everyone uses today, and the one in this course.
:::

Today Python is looked after by the **Python Software Foundation**, a non-profit, and a worldwide team of
mostly volunteer **core developers**, the people allowed to change Python itself. Since 2019 a five-person
**steering council**, elected by those core developers, makes the final decisions. Before that, Guido had the
last word for almost 30 years, with the joke title "Benevolent Dictator For Life", and he stepped down from that
role in July 2018.

:::photo{src="/lesson-images/python/guido-van-rossum.webp" alt="Guido van Rossum, the creator of Python, in 2014" credit="Daniel Stroud" license="CC BY-SA 4.0" source="https://commons.wikimedia.org/wiki/File:Guido-portrait-2014-drc.jpg"}
Guido van Rossum, who created Python, in 2014.
:::

:::usedby{title="Industries"}
- AI and machine learning
- Data science
- Web backends
- Automation and DevOps
- Science and research
- Teaching
:::

:::usedby{title="Used at"}
- Instagram
- YouTube
- Spotify
- Netflix
- Dropbox
- NASA
:::

:::funfact
Python is named after the British comedy show *Monty Python's Flying Circus*, not the snake. And Python
has a hidden poem inside it: "The Zen of Python", 19 short design rules written by Tim Peters, an early core
developer. Press **Run** on the line below, then **Enter** in the terminal, to see its first lines:
:::

```bash run
python3 -c "import this" | head -9
```

```text
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
```

The last line, "Readability counts", is the one this whole course leans on: code is for people to read first.
(Do not worry about what `-c` and `| head -9` mean yet. In short: run this one line of Python, and show only the
first 9 lines of what it prints.)
:::

:::step{type=concept title="Meet the terminal"}
Look at the bottom of your screen. That dark box is the **terminal**: a way to talk to a computer by typing
instructions instead of clicking. It is a real Linux machine, made just for you, and nothing you do here can
break your own computer.

It shows a **prompt** and waits:

```text
learner@python-basics:/workspace$
```

Read it from left to right: you are the user `learner`, on a machine called `python-basics`, in the folder
`/workspace`. A **folder** (also called a directory) is a box that holds files, exactly like the folders on your
own computer. The `$` means "your turn, type something".

:::photo{src="/lesson-images/python/vt100-terminal.webp" alt="A DEC VT100 computer terminal from 1978: a beige screen and keyboard" credit="Jason Scott" license="CC BY 2.0" source="https://commons.wikimedia.org/wiki/File:DEC_VT100_terminal.jpg"}
A DEC VT100 from 1978: a screen and a keyboard wired to one big shared computer. Your terminal window is named after machines like this, and still behaves like one.
:::

Three commands are enough to find your way around:

- `pwd` prints the folder you are in ("print working directory").
- `ls` lists what is in it.
- `cd 01-first-program` moves into that folder ("change directory"). `cd ..` goes back up one level.

Every chapter of this course has its own folder in `/workspace`, numbered like the chapter. Let's look. Press
**Run** on the line below (it types the command for you), then press **Enter** in the terminal:

```bash run
cd /workspace/01-first-program && ls
```

The `&&` between the two commands means "do the first one, and if it worked, do the second". You should see
three files:

```text
first.py  fix_me.py  hello.py
```

The `.py` at the end of a name says "this is a Python file". It is still plain text: you could open it in any
text editor. The same files are in the file list next to the editor; open one with a click.
:::

:::step{type=concept title="A program is a list of instructions" file="01-first-program/first.py" line="2-5"}
Open `first.py`. It is your first real program, and it is tiny:

```python
# Your very first Python file. Python reads it from the top, one line at a time.
print("Python is reading this file, line by line.")
print("2 + 3")
print(2 + 3)
print("That's the end of the file. Bye!")
```

Let's read it like Python does, one line at a time.

1. The first line starts with `#`. That makes it a **comment**: a note for people. Python skips it
   completely. You can write anything after a `#`.
2. `print("Python is reading this file, line by line.")` is an **instruction**. `print` is the name of a
   tool that comes built into Python (a **function**, chapter 2 explains the word), and the round brackets hold
   what you give it. Its job: show that on the screen.
3. The text inside the quotes, `"Python is reading..."`, is called a **string**: a piece of text. The
   quotes are not part of the text; they only show Python where the text starts and stops.

That is the whole idea of programming: write instructions, in an order, in a file. Python does them from the
top to the bottom.

But wait. Look at lines 3 and 4. They look almost the same: `print("2 + 3")` and `print(2 + 3)`. Do you think
they print the same thing? Hold that thought for a moment.
:::

:::step{type=predict title="Guess first"}
:::question
`first.py` has `print("2 + 3")` on one line and `print(2 + 3)` on the next. What do those two lines show?
:::
- [ ] `5` and `5`
- [ ] `2 + 3` and `2 + 3`
- [x] `2 + 3`, then `5`
- [ ] An error, because you cannot print a sum
:::explain
Quotes make a string, and a string is shown exactly as it is written: `2 + 3`, plus sign and all. Without
quotes, `2 + 3` is a calculation, so Python works it out first and prints the answer, `5`. The quotes decide
whether Python *shows* something or *works it out*.
:::
:::

:::step{type=try title="Run your first program" file="01-first-program/first.py" line="1-5"}
Time to see it with your own eyes. Run the file:

```bash run
cd /workspace/01-first-program && python3 first.py
```

`python3` is the name of the program that understands Python. It is called the **interpreter**: a program that
reads your code and carries it out straight away, with no separate preparing step for you to do. `first.py` is
the file you want it to run. Here is what appears:

```text
Python is reading this file, line by line.
2 + 3
5
That's the end of the file. Bye!
```

Four lines on the screen, one for each `print`, in exactly the order they are written in the file. The
comment on line 1 left no trace at all.

So what actually happened in that split second after you pressed Enter? Press Play and watch:

:::diagram{name="python-runs-a-file"}
Python checks the whole file first, then runs it from the top, one line at a time.
:::

Now try something brave: change `print(2 + 3)` to `print(20 * 3)` in the editor, save (Ctrl+S, or Cmd+S on a
Mac), and run the file again. `*` means multiply, so the third line now says `60`. You just changed what a
program does. That is programming.
:::

:::step{type=example title="Worked example: a program that introduces itself"}
Before your first task, here is a program with the same shape. Imagine a little weather program that should
say two lines:

```text
Hi, I am Sunny.
I will tell you if you need an umbrella.
```

Here is the whole program:

```python
print("Hi, I am Sunny.")
print("I will tell you if you need an umbrella.")
```

1. One `print` for each line you want to see. Every `print` starts a new line on its own.
2. Each sentence goes inside quotes, so Python shows it exactly as written: capital letters, spaces and the
   full stop included.
3. The order of the lines in the file is the order on the screen.

That is all. There is no "start" or "end" to write: a Python file simply begins at the top and ends at the
bottom.
:::

:::step{type=task task=hello_pocket title="Your turn: Pocket says hello"}
Open `hello.py`. Right now it only has comments, so it prints nothing at all. Make it print these two lines,
exactly:

```text
Hello! I am Pocket.
I will help you track your money.
```

1. Write one `print(...)` for each line, below the comments.
2. Copy each sentence exactly, with its capital letters and punctuation.
3. Save, then run it to see Pocket talk:

```bash run
cd /workspace/01-first-program && python3 hello.py
```

When the two lines look right, press **Check**.

The usual slips, with what Python says (we tried each one):

- `Print(...)` with a capital P: `NameError: name 'Print' is not defined. Did you mean: 'print'?` Python cares
  about capital letters.
- A space before `print`: `IndentationError: unexpected indent`. A line must start at the very left unless it
  belongs inside something (chapter 4 explains when).
- Curly quotes `“…”` pasted from a document: `SyntaxError: invalid character '“' (U+201C)`. Type plain quotes
  `"` in the editor.
- A missing `)` at the end: `SyntaxError: '(' was never closed`.
:::

:::step{type=concept title="When Python does not understand you" file="01-first-program/fix_me.py" line="2-4"}
Here is a secret every programmer knows: **your programs will have mistakes**. Every single day, for everyone,
from beginners to people who build Python itself. Nobody writes perfect code; good programmers simply get very
good at reading what Python tells them.

And Python tells you a lot. Open `fix_me.py`:

```python
print("Pocket is starting...)
prnt("Ready to count your rupees.")
print("Today's budget is", 500, "rupees.")
```

There are two mistakes in it. Can you spot them before running it? Don't worry if you can't: that is what the
next step is for.

Notice the last line. `print` can take several things separated by commas: a string, a number, another
string. It shows them all on one line, with one space between each: `Today's budget is 500 rupees.` The
apostrophe in `Today's` is fine, because the string is wrapped in double quotes.
:::

:::step{type=try title="Read Python's first message" file="01-first-program/fix_me.py" line="2"}
Run the broken program and let Python explain:

```bash run
cd /workspace/01-first-program && python3 fix_me.py
```

```text
  File "/workspace/01-first-program/fix_me.py", line 2
    print("Pocket is starting...)
          ^
SyntaxError: unterminated string literal (detected at line 2)
```

This is an error message, and it is friendlier than it looks. Read it from the **bottom**:

- `SyntaxError` is the kind of problem. **Syntax** means the grammar of the language: Python could not even
  understand how the line is written.
- `unterminated string literal` means "a piece of text that never ends". The string opened with a quote and
  never closed.
- The line above shows the code, and the `^` points at where the trouble starts: the opening quote.
- The first line says which file and which line: line 2. (Python counts lines from 1, and the comment at the top
  is line 1.)

Here is the curious part. Look at what is *not* on the screen: `Pocket is starting...` was never printed, even
though that line comes first. Remember the diagram? Python checks the grammar of the **whole file before
running anything**. One grammar mistake, anywhere, and not a single line runs.

And the second mistake, `prnt` on line 3? Python has not complained about it yet. That one is not a grammar
mistake, so it can only be found while the program runs. The next step shows it.
:::

:::step{type=example title="Worked example: two kinds of mistakes"}
Suppose you fix the missing quote and run the file again. Python gets further this time:

```text
Pocket is starting...
Traceback (most recent call last):
  File "/workspace/01-first-program/fix_me.py", line 3, in <module>
    prnt("Ready to count your rupees.")
    ^^^^
NameError: name 'prnt' is not defined. Did you mean: 'print'?
```

Something changed! The first line *did* print. So this mistake is a different kind:

1. The grammar is fine now, so Python started running the program, line by line.
2. Line 2 worked and printed `Pocket is starting...`.
3. On line 3 Python met the name `prnt`. It looked for a tool with that name, found none, and stopped:
   `NameError`. Python even guesses what you meant: `Did you mean: 'print'?`

The word **Traceback** at the top means "here is where I was when it happened", and `in <module>` means "in the
main part of the file, not inside a function". You will learn to read long tracebacks in chapter 6.

So there are two moments a mistake can show up:

| When | Kind | What you see |
|---|---|---|
| Before anything runs | `SyntaxError` | Nothing printed, only the error |
| While it runs | `NameError` and friends | The lines before it print, then the error |
:::

:::step{type=task task=fix_first_errors title="Your turn: fix the two mistakes"}
Make `fix_me.py` run from top to bottom and print exactly:

```text
Pocket is starting...
Ready to count your rupees.
Today's budget is 500 rupees.
```

1. Run it and read the last line of Python's message.
2. Fix that one mistake, save, and run it again.
3. Repeat until all three lines appear. Change only the mistakes, not the words.

```bash run
cd /workspace/01-first-program && python3 fix_me.py
```

Then press **Check**.

The usual slips: fixing the quote by deleting the opening one too (then Python sees `Pocket is starting...` as
code and reports `SyntaxError: invalid syntax. Perhaps you forgot a comma?`); changing the words while fixing (the check compares every letter); or
fixing only one mistake and stopping, so press Run again after every fix until all three lines appear.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A file has a missing quote on its very last line. What happens when you run it?
:::
- [ ] Every line runs, then Python stops at the last one
- [x] Nothing runs: Python reports a SyntaxError first
- [ ] Python skips the broken line and runs the rest
:::explain
Python checks the grammar of the whole file before it runs a single line. A syntax mistake anywhere, even at
the very end, stops everything.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `print("Hello" , 7)` show?
:::
- [ ] `"Hello" , 7`
- [x] `Hello 7`
- [ ] `Hello7`
- [ ] An error: you cannot print text and a number together
:::explain
`print` shows each thing you give it, separated by one space, and the quotes are not part of the text. So the
string `Hello` and the number `7` appear as `Hello 7`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Which line of Python does nothing at all when the program runs?
:::
- [ ] `print("")`
- [x] `# print("Hi")`
- [ ] `print(0)`
:::explain
A line that starts with `#` is a comment, a note for people, so Python skips it, even if it looks like code.
`print("")` still prints an empty line, and `print(0)` prints `0`.
:::
:::

:::step{type=deep-dive title="Go deeper: python3, the interpreter and the REPL"}
**Which Python is this?** Ask it:

```bash run
python3 --version
```

On this lab machine it answers `Python 3.12.3`; your own computer may have another version. The program you
have been using is **CPython**, the standard Python, itself written in C. When it "translates to bytecode" (step 3
of the diagram), it turns your lines into a simpler list of instructions for its own **virtual machine**: a small
program inside CPython that works like a pretend computer and carries out those instructions one by one. That is
what people mean when they call Python an **interpreted** language: no separate build step, you just run the
file. (Languages like C and Java have a separate step first, called compiling. You will meet it in the Java course.)

**The REPL.** Type `python3` alone and press Enter. The prompt changes to `>>>`. This is the **REPL** (read,
evaluate, print, loop: it reads one line, works it out, prints the answer, and waits for the next): type `2 + 3`
and Python answers `5` right away, no `print` needed. It is perfect for quick experiments. Type `exit()` to leave.

**Why `print` and not just the text?** In a file, a line like `"hello"` alone is allowed, but it shows nothing:
Python works it out and throws it away. Only `print` sends things to the screen. In the REPL, values are shown
automatically, which is why it feels different.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Find your way in the terminal with `pwd`, `ls` and `cd`, and run a program with `python3 file.py`.
- Write a program as a list of instructions that Python runs from the top, one line at a time.
- Show text and numbers with `print`, and tell a string (in quotes) from a calculation (without).
- Read an error from the bottom: a `SyntaxError` stops everything before it starts; a `NameError` stops the
  program at the line where it happens.

:::photo{src="/lesson-images/python/py-01-sketch.webp" alt="Sketchnote: Your first program. A program is a list of instructions in a file; Python carries them out from the top, one line at a time. Flow: python3 hello.py, check the grammar, run line 1, line 2, print shows text, end of file: stop. Remember: 2 + 3 in quotes is text, without quotes a sum; a line starting with # is a note Python skips; SyntaxError means nothing runs at all; NameError means the lines before it already ran." ai="true"}
One page of notes for this chapter.
:::

Next, chapter 2: your first functions, small named pieces that each do one job.
:::
