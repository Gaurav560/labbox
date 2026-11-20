:::step{type=story title="Why classes"}
A bank has thousands of accounts. Each has an owner and a balance, and each follows the same rules:
no negative deposits, no taking out more than is there. A **class** writes those rules once, and every
account made from it follows them.

:::mission
In `classes/bank.js`, finish a bank account that protects its balance, then make different shapes
work together through one method name.
:::

:::picture{name="passbook" concept="A class is a blueprint"}
Riya and Arjun have separate balances, even though both accounts follow the same rules.
:::
:::

:::step{type=concept title="A class is a blueprint"}
A class is a **blueprint**; the objects made from it are the houses, each with its own contents.

```javascript
class Account {
  constructor(owner) {
    this.owner = owner;     // runs once for each new account
    this.balance = 0;
  }
}

const a = new Account("Riya");
const b = new Account("Arjun");
a.owner   // "Riya", and b.owner is "Arjun"
```

`new` builds an object from the blueprint, and `this` means "the object being built or used".

:::picture{name="blueprint-houses" concept="A class is a blueprint"}
One blueprint, many houses: one class, many objects.
:::
:::

:::step{type=concept title="Methods, and a private balance"}
**Methods** are functions that belong to the class and work on `this`:

```javascript
class Counter {
  #count = 0;              // private: only this class can touch it

  get count() {            // read it like a field: c.count
    return this.#count;
  }

  increment() {
    this.#count += 1;
  }
}
```

A field starting with `#` is **private**: code outside the class cannot change it, so the methods are
the only way in. That is how a class protects its rules.

:::picture{name="bank-counter" concept="Methods, and a private balance"}
The cash stays behind the counter. Each change goes through a method that can check it.
:::
:::

:::step{type=example title="Worked example: a counter that refuses bad steps"}
A method checks before it changes anything:

```javascript
class Steps {
  #total = 0;

  get total() {
    return this.#total;
  }

  add(n) {
    if (!(n > 0)) {
      throw new RangeError(`steps must be positive: ${n}`);  // 1. refuse
    }
    this.#total += n;                                       // 2. then change
  }
}
```

1. Check first, and throw before touching the data.
2. Only a good value changes `#total`, so it can never go wrong.

`deposit` and `withdraw` follow this exact shape.

:::picture{name="step-turnstile" concept="Methods, and a private balance"}
Check the proposed step before touching the stored total.
:::
:::

:::step{type=predict title="Guess first"}
:::question
Using `Steps` above, what happens with `s.total = 100`?
:::
- [ ] The total becomes 100
- [x] Nothing changes: `total` only has a getter
- [ ] It adds 100
- [ ] It resets to 0
:::explain
`total` has a getter and no setter, so assigning to it does nothing (and throws an error in strict
code). The private `#total` can only change through `add`.
:::
:::

:::step{type=try title="Make two objects"}
```bash run
node -e 'class C { #n = 0; get n() { return this.#n; } inc() { this.#n++; } } const a = new C(), b = new C(); a.inc(); a.inc(); b.inc(); console.log(a.n, b.n)'
```

Each object has its own private count.

:::picture{name="independent-dials" concept="A class is a blueprint"}
Turning the first counter twice changes only its own dial.
:::
:::

:::step{type=task task=bank_account title="Warm-up: deposit and withdraw"}
In `classes/bank.js`, finish `deposit` and `withdraw`:

- `deposit(amount)` adds to the balance; an amount that is not positive throws a `RangeError`
- `withdraw(amount)` takes money out; a bad amount, **or more than the balance**, throws a
  `RangeError` and leaves the balance exactly as it was

After `deposit(500)` and `withdraw(200)`, `balance` is `300`.

:::picture{name="withdraw-slip" concept="Methods, and a private balance"}
When a withdrawal is refused, the balance on the slip stays where it was.
:::
:::

:::step{type=concept title="Same method name, different classes"}
Different classes can offer a method with the **same name**, each doing its own version:

```javascript
class Square {
  constructor(side) { this.side = side; }
  area() { return this.side ** 2; }
}

for (const s of [new Square(2), new Rect(3, 4)]) {
  console.log(s.area());   // 4, then 12
}
```

The loop never asks which shape it has: it just calls `area()`. Like a wall socket, anything with the
right plug fits.

:::picture{name="plug-socket" code='area()' concept="Same method name, different classes"}
Anything with the right plug fits the socket.
:::
:::

:::step{type=task task=total_area title="Circles, and the total area"}
In `classes/bank.js`, give `Circle` an `area()` method (`Math.PI` times the radius squared), and make
`totalArea(shapes)` add up every shape's area, rounded to 2 decimals:

- `totalArea([new Rect(3, 4), new Circle(1)])` returns `15.14`
- `totalArea([])` returns `0`

:::picture{name="area-tiles" concept="Same method name, different classes"}
Both shapes report areas in the same square units, so their answers can be added.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `new` do in `new Account("Riya")`?
:::
- [ ] Copies an existing account
- [x] Builds a new object from the class and runs its constructor
- [ ] Creates a new class
- [ ] Nothing: it is optional
:::explain
`new` makes a fresh object and runs `constructor` with `this` set to it.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why make `#balance` private?
:::
- [ ] It makes the code faster
- [x] So only the class's own methods, with their checks, can change it
- [ ] JavaScript requires it
- [ ] So it is not saved
:::explain
Outside code cannot set a negative balance by accident: every change goes through the checks.
:::
:::

:::step{type=deep-dive title="Inheritance and prototypes"}
`class Savings extends Account { ... }` makes a class that starts with everything `Account` has and
adds more; `super(...)` calls the parent's constructor. Use it sparingly: sharing a method name (like
`area`) is often simpler than a family tree of classes.

Under the hood, JavaScript classes are built on **prototypes**: each object has a hidden link to an
object holding the shared methods. `class` (added in 2015) is a clearer way to write that older idea.
:::

:::step{type=recap title="Chapter done"}
- A class is a blueprint; `new` builds objects, `constructor` sets them up, `this` is the object.
- Methods work on `this`; `#private` fields can only change through them.
- Check and throw before changing data, so the object can never go wrong.
- Different classes with the same method name can be used side by side.

:::picture{name="shape-requests" concept="Same method name, different classes"}
One request reaches different shapes. Each shape uses its own measurements to answer.
:::
:::
