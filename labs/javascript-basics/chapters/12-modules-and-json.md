:::step{type=story title="How does a playlist survive closing the app?"}
Everything Mixtape knows lives in memory, and memory is wiped the moment the program ends. To keep a playlist, or to
send it to a friend's phone, it has to leave memory and travel: into a file, across the internet, into a database.
And there is a catch. Files and networks carry **text**, nothing else. Your beautiful objects cannot travel as they
are.

The answer is a text format so simple that it took over the world: **JSON**. Almost every app you use sends and
receives it all day. And a second idea comes with it: once a program grows, its code is split into **modules**, one
file for each job.

:::mission
Write `savePlaylist`, which turns a playlist into JSON text, and `loadPlaylist`, which reads it back.
:::
:::

:::step{type=try title="A module, and the file that uses it" file="12-modules-and-json/library.js" line="2-10"}
Open `library.js`. It is a **module**: a file that shares some of what it has.

```js
function formatLength(seconds) {
  const m = Math.floor(seconds / 60);
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

const secret = "only this file can see me";

module.exports = { formatLength };
```

`module.exports` lists what other files may use. Now open `app.js`, which starts with
`const library = require("./library.js");`, and run it:

```bash run
cd /workspace/12-modules-and-json && node app.js
```

```text
4:05
1:02
undefined
[ 'formatLength' ]
```

`require` loaded the module and gave back exactly what it exported: an object with one function. `formatLength` works
(`padStart(2, "0")` turned 2 seconds into `02`). But `library.secret` is `undefined`: it was never exported, so no
other file can see it. That privacy is the whole point. Every task file in this course ends with `module.exports`,
and that is how LabBox's checks reach your functions.

And now the promise from chapter 2: the other line every task file has. `if (require.main === module) { ... }` asks
"was this file started with `node`, or loaded by someone else's `require`?" `require.main` is the file Node was
started with; `module` is this file. When you type `node playlist.js`, they are the same, so the block runs and prints
the examples. When the Check button `require`s your file, they are different, so the block is skipped and nothing is
printed in the middle of the check.
:::

:::step{type=concept title="require, import, and the node: modules"}
JavaScript has two ways to share code between files, because modules arrived late:

| Style | Share | Use |
|---|---|---|
| CommonJS (Node, since 2009) | `module.exports = { f }` | `const { f } = require("./file.js")` |
| ES modules (the standard, 2015) | `export function f() {}` | `import { f } from "./file.mjs"` |

Browsers and new projects use `import` and `export`; Node supports both (`.mjs` files, or `"type": "module"` in
`package.json`). This course uses `require`, which works in every `.js` file without any setup.

Node also comes with built-in modules, named with `node:` in front: `require("node:fs")` reads and writes files
(chapter 16), and `require("node:test")` runs tests (chapter 17).
:::

:::step{type=try title="An object becomes text, and back" file="12-modules-and-json/json.js" line="2-11"}
Open `json.js` and run it:

```bash run
cd /workspace/12-modules-and-json && node json.js
```

```text
{"name":"Rainy day","songs":[{"title":"Monsoon Drive","seconds":245}],"shuffle":false}
string 86
Monsoon Drive false
{"when":"1970-01-01T00:00:00.000Z"}
{
  "name": "Rainy day",
  "songs": [
    {
      "title": "Monsoon Drive",
      "seconds": 245
    }
  ],
  "shuffle": false
}
```

- `JSON.stringify(playlist)` turned the object into **text**: 86 characters that can go anywhere text can go.
- `JSON.parse(text)` built a **new** object from that text. Same data, but `back === playlist` is `false`: it is a
  different object, like a photocopy.
- Line four is a warning. A `Date` became text, and `skip` (undefined) and `play` (a function) **vanished**. JSON
  only knows text, numbers, true and false, null, arrays and plain objects. (`new Date(0)` is the moment computers
  count time from, midnight on 1 January 1970 in UTC, the world's reference time; the `Z` at the end stands for UTC.)
- `JSON.stringify(playlist, null, 2)` indents it with 2 spaces, for people to read.
:::

:::step{type=concept title="JSON's strict rules"}
JSON looks like JavaScript, but it is stricter:

```json
{ "name": "Rainy day", "count": 1, "songs": [ { "title": "Monsoon Drive" } ] }
```

- Every key in **double quotes**: `{ name: 1 }` is fine JavaScript, but not JSON.
- Text in double quotes only; no single quotes, no trailing commas, no comments.

Break a rule, and `JSON.parse` refuses with a SyntaxError:

```text
SyntaxError: Expected property name or '}' in JSON at position 1 (line 1 column 2)
```

That was `JSON.parse("{name: 1}")`: at position 1, JSON expected a quoted property name. A trailing comma,
`JSON.parse('{"a": 1,}')`, gives `SyntaxError: Expected double-quoted property name in JSON at position 8 (line 1
column 9)` (we tried both on Node 22). Chapter 13 shows how to catch that error instead of crashing.
:::

:::step{type=example title="Worked example: saving a song"}
```js
function saveSong(title, seconds) {
  return JSON.stringify({ title, seconds, minutes: Math.floor(seconds / 60) });
}

saveSong("Neon Lanes", 198)   // '{"title":"Neon Lanes","seconds":198,"minutes":3}'
```

1. Build the object you want to save. `{ title, seconds }` is short for `{ title: title, seconds: seconds }`.
2. Add anything worked out, like `minutes`.
3. `JSON.stringify` it, and give back the **text**.

Your `savePlaylist` task has this shape.
:::

:::step{type=task task=save_playlist title="Your turn: save a playlist"}
Open `playlist.js` and make `savePlaylist(name, songs)` give back **JSON text** of an object with three properties:
`name`, `count` (how many songs there are) and `songs`.

`savePlaylist("Rainy day", [{ title: "Monsoon Drive", seconds: 245 }])` gives
`'{"name":"Rainy day","count":1,"songs":[{"title":"Monsoon Drive","seconds":245}]}'`.

```bash run
cd /workspace/12-modules-and-json && node playlist.js
```

Before you start it prints an empty line and `[]`. Then press **Check**.

The usual slip: building the object and forgetting `JSON.stringify`. The function then gives back an object, not
text (`typeof` says `"object"`), and the check says it should give back text. Also make `count` come from the songs
(`songs.length`): the check tries a playlist of two songs and an empty one.
:::

:::step{type=predict title="Guess first"}
:::question
What is `typeof JSON.stringify({ a: 1 })`?
:::
- [ ] `"object"`
- [x] `"string"`
- [ ] `"json"`
:::explain
JSON is text, so stringify always gives back a string.
:::
:::

:::step{type=task task=load_playlist title="Your turn: load it back"}
In `playlist.js`, make `loadPlaylist(text)` read JSON text and give back the **titles** of its songs, as an array.
Saved files can be old or incomplete: when the JSON has no `songs` at all, give back `[]`.

`loadPlaylist('{"name":"Quiet","songs":[]}')` gives `[]`, and `loadPlaylist('{"name":"Old"}')` gives `[]` too.

`JSON.parse`, then chapter 11's `map`, and chapter 4's `??` for the missing songs.

```bash run
cd /workspace/12-modules-and-json && node playlist.js
```

Then press **Check**.

The usual slip: no `??` for the missing songs. `JSON.parse(text).songs.map(...)` on `'{"name":"Old"}'` crashes with
`TypeError: Cannot read properties of undefined (reading 'map')` (we tried it): there is no `songs`, so there is
nothing to `map`.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
`library.js` has a `const secret` that is not in `module.exports`. What does `require("./library.js").secret` give?
:::
- [ ] The secret
- [x] `undefined`
- [ ] An error
:::explain
Only what a module exports can be used from outside. Everything else stays private to its file.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Which of these is valid JSON?
:::
- [ ] `{ name: "Asha" }`
- [ ] `{ 'name': 'Asha' }`
- [x] `{ "name": "Asha" }`
:::explain
JSON needs double quotes around every key and every piece of text.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What happens to a function stored in an object when you `JSON.stringify` it?
:::
- [ ] It becomes text
- [x] It disappears
- [ ] An error
:::explain
JSON has no functions, so stringify leaves that property out (just like `undefined`).
:::
:::

:::step{type=deep-dive title="Go deeper: package.json, npm and JSON everywhere"}
**package.json.** Every Node project has one: a JSON file with the project's name, its scripts, and the libraries it
needs.

**npm.** The Node package registry, with millions of free packages, more than any other language's: `npm install`
downloads what `package.json` lists into a `node_modules` folder, and `require` finds it there.

**JSON everywhere.** Web APIs answer in JSON, settings files are JSON, and databases like MongoDB store documents that
look just like it. Douglas Crockford named and described JSON in the early 2000s, taking the idea straight from
JavaScript's own object syntax.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Split code into modules: share with `module.exports`, use with `require`, and keep the rest private.
- Tell CommonJS (`require`) from ES modules (`import`), and load Node's built-in `node:` modules.
- Turn objects into JSON text with `JSON.stringify` and back with `JSON.parse`.
- Follow JSON's strict rules, and know what it cannot carry: functions, `undefined`, real dates.

:::photo{src="/lesson-images/javascript/js-12-sketch.webp" alt="Sketchnote: Modules and JSON. A module shares only what it puts in module.exports; JSON turns data into text that can go into a file or across a network. Flow: an object in memory, JSON.stringify(), JSON text, JSON.parse(), a new object. Remember: require() gives back only what was exported; JSON needs double quotes on every key and every text; functions and undefined vanish, a Date becomes text; bad JSON makes JSON.parse throw a SyntaxError." ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 2. Mixtape's data has shape now: strings, arrays, objects, sets, and JSON to save them. Next,
Part 3: real programs, starting with errors you can catch.
:::
