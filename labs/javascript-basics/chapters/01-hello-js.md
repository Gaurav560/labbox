:::step{type=story title="What can ten days of work become?"}
In May 1995, a programmer at Netscape was given ten days to make a small language for web pages. Ten days. He wrote it,
it shipped in the Netscape browser, and today it runs on almost every website, on servers, in phone apps, and inside
the very editor you are looking at. That language is **JavaScript**, and you are going to write it today.

Your project for this whole course is **Mixtape**, a small playlist app: songs, their lengths, shuffles and a
monthly report. Today Mixtape says its very first words.

:::mission
Make Mixtape introduce itself, then fix a program with two mistakes so that it runs.
:::
:::

:::step{type=history title="The story of JavaScript"}
This is **Brendan Eich**, who wrote the first version of JavaScript in ten days at Netscape.

:::photo{src="/lesson-images/javascript/brendan-eich.webp" alt="Brendan Eich, the creator of JavaScript: a smiling man with short grey hair and glasses, in a dark jacket and white shirt" credit="Darcy Padilla" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Brendan_Eich_Mozilla_Foundation_official_photo.jpg"}
Brendan Eich, creator of JavaScript.
:::

Before JavaScript, a web page was a printed sheet: text and pictures, nothing more. Even a form with a missing field
had to travel to the server and back before you learned you had made a mistake. JavaScript let the page itself react,
straight away. It first shipped in this browser, **Netscape Navigator 2**, in 1995:

:::photo{src="/lesson-images/javascript/netscape-navigator-2.webp" alt="The about page of Netscape Navigator version 2.02 on Windows, with the big N logo and the toolbar buttons Back, Forward, Home, Reload, Images, Open, Print, Find and Stop" credit="Indolering" license="CC0" source="https://commons.wikimedia.org/wiki/File:Netscape_Navigator_2_Screenshot.png"}
Netscape Navigator 2: the first browser that ran JavaScript.
:::

:::timeline
- **1995** Brendan Eich writes the first version in ten days at Netscape.
- **1997** The first ECMAScript standard: the official name of the language's rules.
- **2005** Gmail and Google Maps show what JavaScript web apps can do.
- **2009** Ryan Dahl creates **Node.js**: JavaScript outside the browser, on servers and laptops.
- **2015** A big update adds classes, arrow functions, `let` and `const`, and promises.
:::

:::funfact
It was first called **Mocha**, then **LiveScript**. The name **JavaScript** was chosen for marketing, because Java was
popular in 1995. The two languages are about as related as "car" and "carpet".
:::
:::

:::step{type=try title="Run your first program" file="01-hello-js/first.js" line="2-5"}
Open `first.js` in the editor:

```js
console.log("Hello from Mixtape!");
console.log("Today's playlist has 3 songs.");
console.log(3 * 4, "minutes of music");
console.log("Done.");
```

`console.log` means "print this on the console", the text area of the terminal. Now run it. In the terminal below,
type this and press Enter:

```bash run
cd /workspace/01-hello-js && node first.js
```

```text
Hello from Mixtape!
Today's playlist has 3 songs.
12 minutes of music
Done.
```

**Node** is the program that runs JavaScript outside a browser. It read your file and ran the lines **from top to
bottom**, one at a time. Look at line 3: `3 * 4` is not text, it is maths, so Node worked it out first and printed
`12`. The comma puts a space between the two things it prints.
:::

:::step{type=concept title="What node does with your file"}
Typing `node first.js` starts a surprising little journey. Press Play:

:::diagram{name="node-runs-a-file"}
Node reads the whole file, checks its grammar, then runs it line by line; a problem while running stops it there.
:::

Two moments matter, and you will meet both today:

1. **Before anything runs**, Node reads the whole file and checks the grammar: every bracket closed, every quote
   ended. A grammar mistake is a **SyntaxError**, and not a single line runs.
2. **While it runs**, a line can still go wrong: using a name that does not exist, or asking nothing for something.
   That stops the program **at that line**; the lines before it already ran.
:::

:::step{type=try title="A program that stops halfway" file="01-hello-js/crash.js" line="2-6"}
Open `crash.js`. No typos at all:

```js
const playlist = ["Monsoon Drive", "Neon Lanes"];
console.log("Songs:", playlist.length);
const next = playlist[5];
console.log("Next up:", next.toUpperCase());
console.log("This line never runs.");
```

```bash run
cd /workspace/01-hello-js && node crash.js
```

```text
Songs: 2
/workspace/01-hello-js/crash.js:5
console.log("Next up:", next.toUpperCase());
                             ^

TypeError: Cannot read properties of undefined (reading 'toUpperCase')
    at Object.<anonymous> (/workspace/01-hello-js/crash.js:5:30)
```

`Songs: 2` printed, so line 3 ran. Then line 5 crashed. The playlist has 2 songs, so there is no song number 5:
`playlist[5]` gave `undefined`, JavaScript's word for "nothing here". And you cannot make nothing upper case.

Read the error like a detective: the **file and line** (`crash.js:5`), a little `^` under the exact spot, and the
**kind** of problem in one sentence. (The lines starting with `at` are the path Node took to get there; chapter 6
reads them properly.)
:::

:::step{type=example title="Worked example: Mixtape counts down"}
Here is a tiny program, and exactly what it prints:

```js
console.log("Starting in...");
console.log(3);
console.log(2);
console.log(1);
console.log("Play!");
```

```text
Starting in...
3
2
1
Play!
```

1. Each `console.log` prints **one line**, in the order the lines are written.
2. Text goes inside quotes: `"Play!"`. Numbers do not need them.
3. Every line here ends with `;`. JavaScript can often guess where a line ends without it, but writing it makes your
   intention clear, and that is the habit in this course.
:::

:::step{type=task task=hello_mixtape title="Your turn: Mixtape says hello" file="01-hello-js/mixtape.js"}
Open `mixtape.js` and make it print exactly these two lines:

```text
Hello! I am Mixtape.
I will play your songs.
```

```bash run
cd /workspace/01-hello-js && node mixtape.js
```

When it prints those two lines, press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
A file has a missing `)` on line 3 of 4. What does `node` print from lines 1 and 2?
:::
- [ ] Lines 1 and 2, then the error
- [x] Nothing from them: only the SyntaxError
- [ ] Everything except line 3
:::explain
Node checks the grammar of the whole file before running anything, so a SyntaxError means no line runs at all.
:::
:::

:::step{type=try title="Two mistakes, two different errors" file="01-hello-js/fixme.js" line="2-4"}
Open `fixme.js`. It has two mistakes. Run it:

```bash run
cd /workspace/01-hello-js && node fixme.js
```

```text
/workspace/01-hello-js/fixme.js:2
console.log("Mixtape is starting...";
            ^^^^^^^^^^^^^^^^^^^^^^^^

SyntaxError: missing ) after argument list
```

A grammar problem on line 2: the `(` was opened and never closed. Nothing ran. Fix only that, run it again, and the
second mistake shows itself:

```text
Mixtape is starting...
/workspace/01-hello-js/fixme.js:3
consol.log("Ready to play your songs.");
^

ReferenceError: consol is not defined
```

This time line 2 **did** print: the grammar was fine, so the program started, and stopped at line 3. A
**ReferenceError** means "I do not know that name": `consol` is not `console`.
:::

:::step{type=task task=fix_first_errors title="Your turn: fix it until it runs" file="01-hello-js/fixme.js"}
Fix both mistakes in `fixme.js`, one at a time, running the file after each fix. When it works it prints:

```text
Mixtape is starting...
Ready to play your songs.
Songs in the playlist: 12
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `console.log(2 + 3, "songs")` print?
:::
- [ ] `2 + 3 songs`
- [x] `5 songs`
- [ ] `5songs`
:::explain
`2 + 3` is maths, so it becomes `5`, and the comma prints a space between the two values.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which error means "I do not know that name"?
:::
- [ ] SyntaxError
- [x] ReferenceError
- [ ] TypeError
:::explain
A ReferenceError names something that does not exist, like `consol`. A SyntaxError is broken grammar; a TypeError is
doing something a value cannot do, like making `undefined` upper case.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
`node app.js` prints two lines, then a TypeError at line 9. What happened?
:::
- [x] The grammar was fine; the program ran until line 9 went wrong
- [ ] Node found the mistake before running anything
- [ ] Lines 1 to 8 were skipped
:::explain
Output before the error means the program started. Errors found before running (SyntaxErrors) print nothing else.
:::
:::

:::step{type=deep-dive title="Go deeper: the browser's console, Node, and the engine"}
**Your browser runs JavaScript too.** In Chrome, press F12 and open the **Console** tab: type `2 + 3` and press Enter.
Every website you visit runs its JavaScript right there.

**Node** took the JavaScript engine out of Chrome (it is called **V8**) and let it run files on any computer. That is
why the same language now builds web pages, servers and command-line tools.

**ECMAScript.** The official name of JavaScript's rules is ECMAScript, kept by a committee called TC39 with members
from Google, Apple, Microsoft and Mozilla. A new version arrives every year, and old code keeps working.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Run a JavaScript file with `node file.js`, and print with `console.log`.
- Explain that Node checks the whole file's grammar first, then runs it top to bottom.
- Tell a SyntaxError (nothing runs) from errors while running, like a ReferenceError or a TypeError.
- Read an error's file, line and message, and fix one mistake at a time.

:::photo{src="/lesson-images/javascript/js-01-notes.webp" alt="Handwritten notes about a first JavaScript program: node file.js runs it, console.log prints a line, grammar is checked first, SyntaxError means nothing ran, ReferenceError means an unknown name" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 2: functions, so Mixtape can work things out for you.
:::
