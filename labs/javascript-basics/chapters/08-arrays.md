:::step{type=story title="Why does JavaScript sort 10 before 9?"}
Give JavaScript three numbers and ask it to sort them:

```js
[10, 9, 1].sort()
```

```text
[ 1, 10, 9 ]
```

1, then 10, then 9. Not a bug: JavaScript is doing exactly what it was told, just not what you meant. By the end of
this chapter you will know what it was told, and the one small function that fixes it.

A playlist is the most natural thing in the world to store in an **array**: an ordered list of songs, numbered from
0, that grows and shrinks as you add and remove.

:::mission
Write `topN`, which picks the n biggest numbers without disturbing the array it was given, and `unique`, which keeps
each item once.
:::
:::

:::step{type=concept title="Numbered slots"}
An **array** holds values in order, in numbered slots starting at **0**:

```js
const playlist = ["Monsoon Drive", "Neon Lanes"];
playlist[0]        // "Monsoon Drive"
playlist.length    // 2
playlist.push("Slow Sunday");   // add to the end
playlist.pop();                 // remove the last one, and give it back
```

Unlike Java's arrays, a JavaScript array grows and shrinks whenever you like, and can hold any mix of values.

:::picture{name="egg-box" concept="Numbered slots"}
An array is a box of numbered slots, starting at 0.
:::
:::

:::step{type=try title="A playlist that grows and shrinks" file="08-arrays/playlist.js" line="2-5"}
Open `playlist.js` and run it:

```bash run
cd /workspace/08-arrays && node playlist.js
```

```text
[ 'Monsoon Drive', 'Neon Lanes', 'Slow Sunday' ] 3
Monsoon Drive Slow Sunday undefined
[ 'Monsoon Drive', 'Neon Lanes' ]
2 3
```

Line two: `playlist.at(-1)` is the **last** song, counting from the end, and `playlist[9]` is `undefined`. Asking
for a slot that does not exist is not an error in JavaScript: it is just nothing. (Chapter 1's crash came from
using that nothing.)

And line three is strange. The code called `backup.pop()`, not `playlist.pop()`. So why did the **playlist** lose
a song?
:::

:::step{type=concept title="Two names, one array" file="08-arrays/playlist.js" line="7-13"}
Here is the code behind lines three and four:

```js
const backup = playlist;
backup.pop();
console.log(playlist);

const copy = [...playlist];
copy.push("Paper Boats");
console.log(playlist.length, copy.length);
```

`const backup = playlist;` does **not** copy the array. It gives the same array a second name. There is one array,
with two names, so a change through either name shows through both.

`[...playlist]` is different: the spread makes a **new** array with the same songs. Adding to `copy` left `playlist`
at 2 songs. Copy first whenever you want to change something you were only lent: that matters a lot in your first
task.

:::picture{name="envelope-address" concept="Two names, one array"}
Two envelopes with the same address lead to the same house.
:::
:::

:::step{type=try title="The sort mystery, solved" file="08-arrays/sorting.js" line="2-4"}
Open `sorting.js`:

```bash run
cd /workspace/08-arrays && node sorting.js
```

```text
[ 1, 10, 9 ]
[ 1, 9, 10 ]
[ 'Neon', 'Zebra', 'apple' ]
```

Plain `sort()` turns every value into **text** and sorts it like a dictionary. As text, `"10"` comes before `"9"`,
because `"1"` comes before `"9"`, just as "apple" comes before "banana". That is what it was told.

To sort numbers, give `sort` a **compare function**: `(a, b) => a - b`. A negative answer puts `a` first, a positive
one puts `b` first. Line two is correct. (`b - a` sorts biggest first.)

The last line is the same rule for text: capitals have smaller code numbers than small letters, so `"Zebra"` comes
before `"apple"`. And watch out: `sort` **changes the array** it is called on.
:::

:::step{type=example title="Worked example: the n smallest, without damage"}
```js
function bottomN(numbers, n) {
  const copy = [...numbers];
  copy.sort((a, b) => a - b);
  return copy.slice(0, n);
}

const marks = [72, 45, 90, 66];
bottomN(marks, 2)   // [45, 66]
marks               // still [72, 45, 90, 66]
```

1. Copy first, because `sort` changes the array in place, and `marks` belongs to the caller.
2. Sort the copy with a compare function, smallest first.
3. `slice(0, n)` gives the first n items. Asking for more than there are just gives them all.
:::

:::step{type=predict title="Guess first"}
:::question
What does `[3, 20, 100].sort()` give?
:::
- [ ] `[3, 20, 100]`
- [x] `[100, 20, 3]`
- [ ] `[3, 100, 20]`
:::explain
As text, `"100"` starts with `1`, `"20"` with `2` and `"3"` with `3`, so the dictionary order is 100, 20, 3.
:::
:::

:::step{type=task task=top_n title="Your turn: the n biggest numbers"}
Open `arrays.js` and make `topN(numbers, n)` give back the n biggest numbers, **biggest first**, without changing the
array it was given.

`topN([72, 45, 90, 66], 2)` gives `[90, 72]`, and `topN([5, 1], 5)` gives `[5, 1]`.

```bash run
cd /workspace/08-arrays && node arrays.js
```

Then press **Check**.
:::

:::step{type=concept title="Searching an array"}
Two questions you will ask arrays all the time:

```js
const playlist = ["Monsoon Drive", "Neon Lanes"];
playlist.includes("Neon Lanes")    // true: is it in there?
playlist.indexOf("Neon Lanes")     // 1: where is it? (-1 when missing)
```

To build a new array as you go, start empty and `push` what you want to keep.

:::picture{name="search-signs" concept="Searching an array"}
A membership question gives yes or no. A position question gives a slot number.
:::
:::

:::step{type=task task=unique title="Your turn: each item once"}
In `arrays.js`, make `unique(items)` give back each item once, in the order it first appears.

`unique(["jelly", "cookie", "jelly", "mint"])` gives `["jelly", "cookie", "mint"]`, and `unique([])` gives `[]`.

```bash run
cd /workspace/08-arrays && node arrays.js
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
After `const b = a; b.push(1);`, has `a` changed?
:::
- [x] Yes: `a` and `b` are one array
- [ ] No: `b` is a copy
:::explain
`=` gives the same array a second name. `[...a]` would make a copy.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `["a", "b", "c"].at(-1)`?
:::
- [ ] `"a"`
- [x] `"c"`
- [ ] `undefined`
:::explain
Negative positions count from the end: -1 is the last item.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What is `[5, 1, 10].sort((a, b) => a - b)`?
:::
- [x] `[1, 5, 10]`
- [ ] `[1, 10, 5]`
- [ ] `[10, 5, 1]`
:::explain
With a compare function, numbers are compared as numbers.
:::
:::

:::step{type=deep-dive title="Go deeper: toSorted, splice and holes"}
**toSorted.** Newer JavaScript has `toSorted`, `toReversed` and `with`, which give back a new array and never touch
the old one: `marks.toSorted((a, b) => a - b)`.

**splice.** `playlist.splice(1, 1)` removes one item at position 1, in place. `slice` (with no "p") copies; `splice`
changes. Everyone mixes them up once.

**Holes.** `const a = []; a[5] = "x";` makes an array of length 6 with five empty slots. Avoid it: keep arrays
packed, and use `push`.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Read and change arrays by position, from the front or from the end with `at(-1)`.
- Grow and shrink them with `push` and `pop`, and search them with `includes` and `indexOf`.
- Copy an array with `[...array]` before changing it, because `=` only adds a second name.
- Sort numbers correctly with `(a, b) => a - b`, and explain why plain `sort()` puts 10 before 9.

:::photo{src="/lesson-images/javascript/js-08-notes.webp" alt="Handwritten notes about JavaScript arrays: slots start at 0, push and pop, at minus 1 is the last, equals gives a second name, spread makes a copy, sort compares as text unless you give a - b" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 9: objects, so a song can carry its title, length and likes together.
:::
