:::step{type=story title="What is this?"}
Mixtape has hundreds of songs, and every one needs the same things: a title, a length, a count of plays, a way to be
played. Writing an object by hand for each would be madness. A **class** is a blueprint: write it once, and build as
many songs from it as you like, each with its own data.

Classes bring one strange little word with them: `this`. Inside a song, `this` means "the song I am". Simple, until
you hand a song's method to someone else, and `this` suddenly means nothing at all. It is one of JavaScript's most
famous surprises, and you will make it happen on purpose today.

:::mission
Finish a `BankAccount` that refuses bad amounts, then give `Circle` an `area()` so `totalArea` can add up any mix of
shapes.
:::
:::

:::step{type=concept title="A class is a blueprint"}
A class describes what every object of its kind has and can do:

```js
class Song {
  constructor(title, seconds) {
    this.title = title;
    this.seconds = seconds;
  }
}

const a = new Song("Neon Lanes", 198);
```

- `constructor` runs once for each new object; `this` is the brand-new object being built.
- `new Song(...)` makes an object from the blueprint. Its `title` and `seconds` are its own.

:::picture{name="blueprint-houses" concept="A class is a blueprint"}
One blueprint, many houses, each with its own furniture.
:::
:::

:::step{type=try title="Two songs, two play counts" file="14-classes/song.js" line="2-26"}
Open `song.js`. The class also has a method, a **private** field and a getter:

```js
class Song {
  #plays = 0;

  play() {
    this.#plays = this.#plays + 1;
    return `${this.title}: play number ${this.#plays}`;
  }

  get plays() {
    return this.#plays;
  }
}
```

```bash run
cd /workspace/14-classes && node song.js
```

```text
Neon Lanes: play number 1
Neon Lanes: play number 2
Slow Sunday: play number 1
2 1 Neon Lanes
undefined function
```

Each song counts its own plays: two for Neon Lanes, one for Slow Sunday. `#plays` starts with `#`, which makes it
**private**: only code inside the class can touch it, so nobody can set a song's plays to -40. The getter `plays` lets
the outside **read** it, as if it were a property. And the last line: `typeof Song` is `"function"`. Underneath, a
class is a special kind of function.
:::

:::step{type=concept title="Methods, and a private balance"}
Private fields are how an object **protects itself**. A bank account keeps its balance private and offers only two
ways to change it, both of which check the amount first:

```js
class BankAccount {
  #balance = 0;

  get balance() {
    return this.#balance;
  }

  deposit(amount) {
    // check, then change #balance
  }
}
```

From outside, `account.#balance = 1000000` is a SyntaxError. The only door is `deposit`, and `deposit` decides who
gets in.

:::picture{name="bank-counter" concept="Methods, and a private balance"}
You cannot reach into the vault; the clerk at the counter checks every request.
:::
:::

:::step{type=example title="Worked example: a volume knob that refuses nonsense"}
```js
class Volume {
  #level = 5;

  get level() {
    return this.#level;
  }

  set(level) {
    if (!Number.isInteger(level) || level < 0 || level > 10) {
      throw new RangeError(`volume must be 0 to 10, not ${level}`);
    }
    this.#level = level;
  }
}
```

1. The level is private, readable through a getter.
2. `set` checks **first** and throws (chapter 13) when the value is bad.
3. Only then does it change the field, so a refused call leaves the volume exactly as it was.

Your `BankAccount` has the same shape, with `deposit` and `withdraw`.
:::

:::step{type=task task=bank_account title="Your turn: an account that refuses bad amounts"}
Open `bank.js` and finish `deposit` and `withdraw`:

- `deposit(amount)` adds the amount; zero or a negative amount throws a **RangeError**.
- `withdraw(amount)` takes it out; a zero or negative amount, or more than the balance, throws a **RangeError** and
  leaves the balance as it was.

After `deposit(500)` and `withdraw(200)`, `balance` is `300`.

```bash run
cd /workspace/14-classes && node bank.js
```

Then press **Check**.
:::

:::step{type=try title="The method that forgot its object" file="14-classes/lostthis.js" line="13-22"}
Now the famous surprise. Open `lostthis.js`:

```js
const p = new Player("Mixtape");
console.log(p.hello());

const later = p.hello;
console.log(later());
```

```bash run
cd /workspace/14-classes && node lostthis.js
```

```text
Mixtape says hello
TypeError: Cannot read properties of undefined (reading 'name')
Mixtape says hello
```

`p.hello()` worked. But `const later = p.hello` copied **just the function**, without its object. In JavaScript,
`this` is decided by **how a function is called**, not where it was written: `p.hello()` has `p` before the dot, so
`this` is `p`. `later()` has nothing before the dot, so `this` is `undefined`, and `undefined.name` crashes.

This bites when you pass a method to something else, like a timer or a button. The fix on the last line,
`p.hello.bind(p)`, makes a copy of the function with `this` tied to `p` forever. (An arrow function
`() => p.hello()` works too.)
:::

:::step{type=predict title="Guess first"}
:::question
`a` and `b` are two `new BankAccount("Riya")`. After `a.deposit(500)`, what is `b.balance`?
:::
- [ ] `500`
- [x] `0`
- [ ] An error
:::explain
Each `new` makes a separate object, with its own private balance.
:::
:::

:::step{type=concept title="Same method name, different classes"}
Different classes can offer a method with the **same name**, each doing its own version:

```js
class Square {
  constructor(side) { this.side = side; }
  area() { return this.side ** 2; }
}

for (const s of [new Square(2), new Rect(3, 4)]) {
  console.log(s.area());   // 4, then 12
}
```

The loop never asks which shape it has: it just calls `area()`. Like a wall socket, anything with the right plug fits.
That idea is called **polymorphism**.

:::picture{name="plug-socket" code='area()' concept="Same method name, different classes"}
Anything with the right plug fits the socket.
:::
:::

:::step{type=task task=total_area title="Your turn: circles, and the total area"}
In `bank.js`, give `Circle` an `area()` method (`Math.PI` times the radius squared), and make `totalArea(shapes)` add up
every shape's area, rounded to 2 decimals.

`totalArea([new Rect(3, 4), new Circle(1)])` gives `15.14`, and `totalArea([])` gives `0`.

```bash run
cd /workspace/14-classes && node bank.js
```

Then press **Check**.
:::

:::step{type=try title="A podcast is a kind of track" file="14-classes/podcast.js" line="2-30"}
One more tool. Open `podcast.js`: a `Podcast` **extends** `Track`, so it gets everything a track has, and changes only
what is different:

```bash run
cd /workspace/14-classes && node podcast.js
```

```text
Neon Lanes 3 min
Night Shift 46 min episode
true
```

`super(title, seconds)` runs the parent's constructor. `label()` was written once, in `Track`, but for the podcast it
called the **podcast's** `length()`: the object decides which version runs, polymorphism again. And a podcast is
`instanceof Track`, because it is one.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What makes a field private in a JavaScript class?
:::
- [ ] The word `private`
- [x] A `#` at the start of its name
- [ ] Writing it in capitals
:::explain
`#balance` can only be used inside the class. Outside, even reading it is a SyntaxError.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
`const f = song.play; f();` What is `this` inside `play`?
:::
- [ ] `song`
- [x] `undefined`
- [ ] The class `Song`
:::explain
`this` comes from the call: `f()` has nothing before the dot. Use `song.play.bind(song)` to keep it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `super(title, seconds)` do inside a child class's constructor?
:::
- [x] Runs the parent class's constructor
- [ ] Makes the object private
- [ ] Copies the parent class
:::explain
The parent sets up its part of the object first; then the child adds its own.
:::
:::

:::step{type=deep-dive title="Go deeper: prototypes, static and arrow methods"}
**Prototypes.** Before 2015, JavaScript had no `class` keyword. Objects shared methods through a **prototype**, a
hidden link to another object. `class` is a friendlier way to write exactly that; it is still prototypes underneath.

**static.** `static fromJSON(text) { ... }` belongs to the class itself: `Song.fromJSON(text)`, not `a.fromJSON`.

**Arrow methods.** `` hello = () => `${this.name} says hello`; `` written as a field keeps `this` forever, because arrow
functions take `this` from where they were written. Many React and Node projects use them for exactly that reason.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write a class with a constructor, methods, private `#` fields and getters, and build objects with `new`.
- Protect an object's data: check first, throw on bad input, only then change.
- Explain why `this` gets lost when a method is passed around, and fix it with `bind` or an arrow.
- Use the same method name across classes, and share code with `extends` and `super`.

:::photo{src="/lesson-images/javascript/js-14-notes.webp" alt="Handwritten notes about JavaScript classes: class is a blueprint, new makes an object, hash makes a field private, this depends on how it is called, bind keeps this, extends and super" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: promises, async and await, and the order in which JavaScript really runs your code.
:::
