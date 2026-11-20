:::step{type=story title="Welcome to JavaScript"}
Every website you use runs JavaScript: the button that likes a post, the map you drag, the form that
warns you before you send it. Today it also runs servers, phone apps and desktop apps like VS Code. In
this course you start from the very first line, with plain examples and real tests checking your work.

:::mission
Write two small functions in `hello/hello.js`: one builds a greeting, the other turns hours and minutes
into minutes.
:::
:::

:::step{type=history title="The story of JavaScript"}
JavaScript was written in ten days, and grew into the most used programming language in the world.

:::before{title="Before JavaScript"}
In the early 1990s a web page was a **printed sheet**: text and pictures, nothing more. Every click went
back to a server, over slow dial-up lines. Even a form with a missing field had to travel to the
server and back before you learned you had made a mistake.
:::

:::solved
**Code that runs inside the browser.** Pages could react straight away: check a form before sending it,
open a menu, update part of the page. Later, with **Node.js**, the same language moved to servers too,
so one language could run a whole web product.
:::

JavaScript was created by **Brendan Eich** at **Netscape** in May 1995. It is standardised as
**ECMAScript** by the **TC39** committee (members include Google, Apple, Microsoft and Mozilla), with a
new version every year.

:::timeline
- **1995** Brendan Eich writes the first version in ten days at Netscape.
- **1997** The first ECMAScript standard is published.
- **2005** Ajax: Gmail and Google Maps show what web apps can do.
- **2009** Ryan Dahl creates Node.js: JavaScript on servers.
- **2015** ES2015 adds classes, arrow functions, let and const, and promises.
:::

:::usedby{title="Industries"}
- Every website
- Web apps
- Servers and APIs
- Mobile apps
- Desktop apps
- Games in the browser
:::

:::usedby{title="Used at"}
- Google (Gmail, Maps)
- Netflix
- PayPal
- LinkedIn
- Uber
- VS Code and Slack
:::

:::funfact
It was first called **Mocha**, then **LiveScript**. The name **JavaScript** was chosen for marketing,
because Java was popular in 1995. The two languages are about as related as "car" and "carpet".
:::
:::

:::step{type=concept title="Why functions exist"}
Imagine writing the same steps every time you greet a customer. If the greeting changes, you would
have to hunt down every copy.

A **function** solves this. You write the steps **once**, give them a name, and use that name whenever
you need them. Change the function, and every place that uses it changes too.

:::picture{name="recipe-card"}
A function is a recipe card: name, inputs, steps, result.
:::
:::

:::step{type=concept title="A function, part by part"}
Here is a complete JavaScript function:

```javascript
function square(x) {
  return x * x;
}

square(4)   // 16
```

- `function` says "here comes a function".
- `square` is its **name**.
- `(x)` is its **input**: inside the function, the value is called `x`.
- `return x * x;` sends the answer back to whoever **called** it.

Calling `square(4)` runs the steps with `x` set to `4`.
:::

:::step{type=example title="Worked example: a function that builds text"}
A function that gives back text, with a **template literal**:

```javascript
function welcome(city) {
  return `Welcome to ${city}!`;
}

welcome("Pune")   // "Welcome to Pune!"
```

1. Template literals use **backticks** (the key above Tab), not quotes.
2. `${city}` puts the value of `city` into the text.
3. `return` hands the finished text back.

Your first task has exactly this shape, with different words.
:::

:::step{type=predict title="Guess first"}
:::question
Open `hello/hello.js`. Right now `greet` says `return "";`. What does `greet("Asha")` give?
:::
- [ ] `"Hello, Asha!"`
- [x] `""`, an empty string
- [ ] `undefined`
- [ ] An error
:::explain
The function runs, and returns exactly what its `return` line says: an empty string. That is why the
starter does not pass yet: it gives back nothing useful.
:::
:::

:::step{type=try title="Run a file with node"}
The terminal at the bottom is a real Linux machine with your files in `/workspace`. `node` runs a
JavaScript file:

```bash run
node hello/hello.js
```

You should see an empty line. Once `greet` works, the same command prints `Hello, Asha!`.
:::

:::step{type=task task=greet title="Warm-up: greet someone"}
Make `greet(name)` return `"Hello, <name>!"`: `greet("Asha")` gives `"Hello, Asha!"`. Mind the comma,
the space and the exclamation mark: the tests compare the text exactly.

:::why
Returning the text (instead of printing it) lets other code reuse it: a web page, a message, or the
tests that check your work.
:::
:::

:::step{type=concept title="Numbers and arithmetic"}
Functions often calculate. JavaScript does arithmetic like school maths:

```javascript
2 + 3 * 4     // 14: * before +
(2 + 3) * 4   // 20: brackets first
10 / 4        // 2.5
7 % 3         // 1: the remainder
```

A function can take **two** inputs, separated by a comma: `function add(a, b) { return a + b; }`.

:::mistake
`+` also joins text: `"2" + "3"` is `"23"`, not `5`. Chapter 2 explains why, and how to stay safe.
:::
:::

:::step{type=task task=total_minutes title="Hours and minutes"}
Make `totalMinutes(hours, minutes)` return the total number of minutes:

- `totalMinutes(2, 15)` returns `135`
- `totalMinutes(0, 45)` returns `45`
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
`function twice(n) { return n * 2; }` What does `twice(7)` give back?
:::
- [ ] `7`
- [x] `14`
- [ ] `72`
- [ ] Nothing: it does not print anything
:::explain
`n` is 7 inside the function, and `return n * 2` hands back `14`. A function can give back a value
without printing anything: the caller decides what to do with it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
What does `` `Hi, ${"Riya"}!` `` give?
:::
- [ ] `"Hi, ${Riya}!"`
- [x] `"Hi, Riya!"`
- [ ] `"Hi, "Riya"!"`
- [ ] An error
:::explain
Inside backticks, `${...}` is replaced by the value inside it.
:::
:::

:::step{type=deep-dive title="Where JavaScript runs"}
In a browser, JavaScript runs inside an **engine** such as V8 (Chrome), SpiderMonkey (Firefox) or
JavaScriptCore (Safari). **Node.js** takes Google's V8 engine out of the browser so JavaScript can read
files, talk to databases and run servers, which is how it runs in your terminal here.

The engines are fast because of **just-in-time compilation**: they watch which code runs most and turn
it into machine code while the program runs.

`module.exports` at the bottom of each file shares your functions with other files, including the
hidden tests. Keep it there.
:::

:::step{type=recap title="Chapter done"}
- A function is a named set of steps: `function name(inputs) { ... }`.
- `return` hands a value back to whoever called the function.
- Template literals use backticks and `${...}` to build text.
- `node file.js` runs a file in the terminal.
:::
