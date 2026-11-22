:::step{type=story title="How do you play a thousand songs without writing a thousand lines?"}
Mixtape has three songs today. Next week it might have three hundred. You cannot write a `console.log` for each one:
you do not even know how many there will be.

A **loop** runs the same lines again and again, once for each song, or until a job is done. With a loop, three lines
of code handle three songs or three million. Today you meet the two loops you will use every single day.

:::mission
Write `sumTo`, which adds up 1 to n, and `countVowels`, which counts the vowels in a song title.
:::
:::

:::step{type=try title="A running total, song by song" file="05-loops/queue.js" line="2-9"}
Open `queue.js`:

```js
const titles = ["Monsoon Drive", "Neon Lanes", "Slow Sunday"];
const seconds = [245, 198, 312];

let total = 0;
for (let i = 0; i < seconds.length; i++) {
  total = total + seconds[i];
  console.log(`${titles[i]}: ${total} seconds so far`);
}
```

```bash run
cd /workspace/05-loops && node queue.js
```

```text
Monsoon Drive: 245 seconds so far
Neon Lanes: 443 seconds so far
Slow Sunday: 755 seconds so far
Up next: Monsoon Drive
Up next: Neon Lanes
Up next: Slow Sunday
```

Three songs, one block of code, run three times. `total` grew each time round: 245, then 443, then 755. That pattern,
start at 0 and add inside the loop, adds up prices, marks and minutes everywhere.
:::

:::step{type=concept title="Repeating with a counter"}
The `for` loop has three parts, separated by `;`:

```js
for (let i = 0; i < seconds.length; i++) {
  // runs once for each i
}
```

1. `let i = 0` runs once, at the start: positions begin at 0.
2. `i < seconds.length` is checked **before every lap**; when it is false, the loop ends.
3. `i++` (add 1 to `i`) runs **after every lap**.

So `i` is 0, 1, 2, and then 3 fails the check. Three laps for three songs.

:::picture{name="running-track" concept="Repeating with a counter"}
The counter marks each lap until the runner reaches the finish line.
:::
:::

:::step{type=concept title="for...of: each item, no counter" file="05-loops/queue.js" line="11-13"}
When you do not need the position, there is a simpler loop:

```js
for (const title of titles) {
  console.log("Up next:", title);
}
```

`for...of` hands you **each item in turn**: no counter, no `.length`, nothing to get wrong. That is the last three
lines of the output above. Use it whenever you only need the items.

:::picture{name="postman" concept="for...of: each item, no counter"}
The postman visits every house in the street, one after another.
:::
:::

:::step{type=example title="Worked example: count the passing marks"}
```js
function countPassing(marks) {
  let count = 0;
  for (const mark of marks) {
    if (mark >= 40) {
      count = count + 1;
    }
  }
  return count;
}

countPassing([72, 35, 40, 90])   // 3
```

:::trace{title="countPassing([72, 35, 40, 90])"}
| mark | mark >= 40? | count |
|---|---|---|
| 72 | yes | 1 |
| 35 | no | 1 |
| 40 | yes | 2 |
| 90 | yes | 3 |
:::

1. Start the counter at 0, before the loop.
2. Inside the loop, decide (chapter 4) and add one when it fits.
3. Return the counter **after** the loop, once every item has been looked at.
:::

:::step{type=predict title="Guess first"}
:::question
`for (let i = 1; i <= 3; i++) { total = total + i; }` starts with `total = 0`. What is `total` after the loop?
:::
- [ ] `3`
- [x] `6`
- [ ] `10`
:::explain
`i` is 1, 2 and 3 (`<=` includes 3), so the total is 1 + 2 + 3 = 6.
:::
:::

:::step{type=task task=sum_to title="Your turn: add up 1 to n"}
Open `loops.js` and make `sumTo(n)` give back 1 + 2 + ... + n. When `n` is 0 or less, give back `0`.

`sumTo(5)` gives `15`, `sumTo(100)` gives `5050`, and `sumTo(0)` gives `0`.

```bash run
cd /workspace/05-loops && node loops.js
```

Then press **Check**.
:::

:::step{type=concept title="Looking at text one character at a time"}
Text is a row of characters, and `for...of` walks through it too:

```js
for (const ch of "Neon") {
  console.log(ch);   // N, then e, then o, then n
}
```

To treat capitals and small letters the same, change the whole text first: `"Neon".toLowerCase()` is `"neon"`. And
`"aeiou".includes(ch)` asks whether one character is a vowel.

:::picture{name="case-lenses" concept="Looking at text one character at a time"}
Look at each letter through the same lens, so A and a count the same.
:::
:::

:::step{type=task task=count_vowels title="Your turn: count the vowels"}
In `loops.js`, make `countVowels(text)` count the vowels (a, e, i, o, u) in either case.

`countVowels("Hello World")` gives `3`, `countVowels("AEIOU")` gives `5`, and `countVowels("rhythm")` gives `0`.

```bash run
cd /workspace/05-loops && node loops.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
How many times does `for (let i = 0; i < 4; i++)` run its block?
:::
- [ ] 3
- [x] 4
- [ ] 5
:::explain
`i` is 0, 1, 2 and 3: four laps. At 4 the check `i < 4` fails.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which loop is best for "print every song title"?
:::
- [x] `for (const title of titles)`
- [ ] `for (let i = 0; i <= titles.length; i++)`
:::explain
`for...of` needs no counter. And the second loop has a bug: `<=` goes one step past the end, to `undefined`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Where should `let total = 0` go, to add up a list?
:::
- [x] Before the loop
- [ ] Inside the loop
:::explain
Inside the loop, it would be reset to 0 on every lap, and only the last item would count.
:::
:::

:::step{type=deep-dive title="Go deeper: while, break, and the loop that never ends"}
**while.** Repeats while a condition is true, for when you do not know the count in advance:
`while (queue.length > 0) { play(queue.shift()); }`.

**break and continue.** `break` leaves the loop at once; `continue` skips to the next lap. Chapter 13 uses
`continue` to skip bad lines in a file.

**The loop that never ends.** Forget the `i++`, and `i` stays 0 forever: the program hangs. In the terminal, press
**Ctrl + C** to stop it. Every programmer does this at least once.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Repeat with a counting `for` loop, and read its three parts.
- Walk through every item, or every character, with `for...of`.
- Keep a running total or a count: start before the loop, add inside, return after.
- Stop a runaway loop with Ctrl + C.

:::photo{src="/lesson-images/javascript/js-05-notes.webp" alt="Handwritten notes about JavaScript loops: for with let i equals 0, check before every lap, i plus plus, for of gives each item, start the total before the loop, Ctrl C stops a stuck loop" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 6: finding bugs, the detective work every programmer does every day.
:::
