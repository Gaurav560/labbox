:::step{type=story title="Why can a function not make your parcel heavier?"}
Parcel has a function that adds a 2 kg box to a parcel. Inside the function, the weight goes from 4 to 6. Back outside,
the parcel still weighs 4. The function did its job, printed proof of it, and the parcel never changed.

Where did the 2 kg go? The answer is the single most important idea about data in Go: when you pass a value to a
function, Go hands over a **copy**. To change the original, you need its **address**: a **pointer**. Pointers sound
scary; by the end of this chapter they will be one small `&` and one small `*`.

:::mission
Fix a wallet whose `Deposit` never changes the balance, then write `Swap`, which exchanges two values through their
addresses.
:::
:::

:::step{type=try title="The box that vanished" file="11-pointers/copy.go" line="10-29"}
Open `copy.go`:

```go
func addBox(p Parcel) {
	p.Weight += 2
	fmt.Println("inside addBox:", p.Weight)
}

func addBoxReally(p *Parcel) {
	p.Weight += 2
}
```

```bash run
cd /workspace/11-pointers && go run copy.go
```

```text
inside addBox: 6
after addBox: 4
after addBoxReally: 6
6 {6} true
```

`addBox` received a **copy** of the parcel and made the copy heavier, which was thrown away when the function ended.
`addBoxReally` received the parcel's **address**, `&parcel`, and changed the real one.
:::

:::step{type=concept title="& and *"}
Two small symbols are all there is:

- `&parcel` means "the address of parcel": a **pointer**, of type `*Parcel`.
- `*ptr` means "the value at that address". For structs, Go lets you skip it: `ptr.Weight` is short for
  `(*ptr).Weight`.

The last line of the output shows all three: `ptr.Weight` is 6, `*ptr` is the whole parcel `{6}`, and `ptr == &parcel`
is `true`, because it points at the very same parcel.

Copies are the safe default: a function cannot change your data behind your back. Pointers are how you say "yes, you
may change this one".

:::picture{name="envelope-address"}
A pointer is an address: whoever has it can find the real house.
:::

A pointer is like this signpost: it is not the town, it tells you where the town is. Follow it, and you reach the
real place, so whatever you change there, everyone else who follows the sign will see.

:::photo{src="/lesson-images/go/signpost.webp" alt="A green finger signpost on a grass verge, with arms pointing to Shipton-on-Cherwell, Tackley, Oxford and the town centre" credit="Jaggery" license="CC BY-SA 2.0" source="https://commons.wikimedia.org/wiki/File:Directions_and_distances_signpost,_Woodstock_-_geograph.org.uk_-_4533617.jpg"}
A signpost in Woodstock: it points at places, it is not the places.
:::
:::

:::step{type=concept title="Methods with a pointer receiver"}
A method can be attached to a type (chapter 12 does a lot more of this). Its **receiver** is the value it works on:

```go
func (w Wallet) Show() int     { return w.Balance }   // a copy: fine for reading
func (w *Wallet) Add(n int)    { w.Balance += n }     // a pointer: needed to change it
```

Use a pointer receiver when a method **changes** the value. Go calls pointer methods on ordinary variables for you:
`w.Add(50)` becomes `(&w).Add(50)` automatically.
:::

:::step{type=task task=deposit title="Your turn: fix Deposit"}
Open `wallet.go`. `Deposit` does not work: the balance never changes. Fix it, so that

```go
w := Wallet{Balance: 100}
w.Deposit(50)
w.Deposit(25)
```

leaves `w.Balance` at `175`. Change as little as possible: one character is enough.

```bash run
cd /workspace/11-pointers && go run run.go
```

Then press **Check**.
:::

:::step{type=example title="Worked example: double a number in place"}
```go
func Double(n *int) {
	*n = *n * 2
}

x := 21
Double(&x)
// x is now 42
```

1. The parameter is `*int`: the address of an int.
2. `*n` reads the value at that address, and `*n = ...` writes back to it.
3. The caller passes `&x`. Inside `Double`, `n` is a copy of the **address**, but it points at the real `x`.
:::

:::step{type=predict title="Guess first"}
:::question
`func reset(n int) { n = 0 }`, then `x := 5; reset(x)`. What is `x`?
:::
- [x] `5`
- [ ] `0`
:::explain
`reset` got a copy of 5 and zeroed the copy. To change `x`, take `n *int` and pass `&x`.
:::
:::

:::step{type=task task=swap title="Your turn: swap two values"}
In `wallet.go`, make `Swap(a, b *int)` exchange the two values: after `Swap(&x, &y)` with `x, y := 1, 2`, `x` is 2 and `y`
is 1. `Swap(&x, &x)` must leave `x` unchanged.

```bash run
cd /workspace/11-pointers && go run run.go
```

Then press **Check**.
:::

:::step{type=try title="A pointer to nothing" file="11-pointers/nilptr.go" line="12-16"}
A pointer that points at nothing is `nil`. Open `nilptr.go`:

```bash run
cd /workspace/11-pointers && go run nilptr.go
```

```text
true
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0x499e91]
```

Asking a `nil` pointer for a field panics. It is Go's most common panic, and the fix is always the same idea: check
`if p == nil` before using a pointer you were handed, or make sure it never is nil.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is the type of `&parcel`, when `parcel` is a `Parcel`?
:::
- [ ] `Parcel`
- [x] `*Parcel`
- [ ] `&Parcel`
:::explain
`&` takes an address; the type of an address of a `Parcel` is written `*Parcel`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
When should a method have a pointer receiver?
:::
- [x] When it changes the value it is called on
- [ ] Always
- [ ] Never
:::explain
A value receiver works on a copy; changes would be lost. Reading-only methods are fine with either.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `p.Weight` do when `p` is a nil `*Parcel`?
:::
- [ ] Gives 0
- [x] Panics: nil pointer dereference
:::explain
There is no parcel at a nil address. Check `p == nil` first.
:::
:::

:::step{type=deep-dive title="Go deeper: new, escape analysis and when not to use pointers"}
**new.** `p := new(Parcel)` makes a zero `Parcel` and gives its address, the same as `&Parcel{}`.

**No pointer arithmetic.** Unlike C, Go will not let you add to an address and wander through memory. Pointers in Go
are safe: they point at a real value or at nil.

**Escape analysis.** Returning `&localVariable` is fine in Go: the compiler notices and keeps the value alive. In C, it
would be a classic bug.

**When not to.** Slices and maps already share their data (chapters 9 and 10), so you rarely need a pointer to them.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain that Go passes copies, so a function cannot change your value without its address.
- Use `&` to take an address and `*` to read or write through it.
- Choose a pointer receiver for methods that change their value.
- Recognise a nil pointer panic, and guard against it.

:::photo{src="/lesson-images/go/go-11-notes.webp" alt="Handwritten notes about Go pointers: functions get a copy, ampersand takes the address, star reads or writes through it, pointer receiver to change, a nil pointer panics, check p equals nil" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 12: methods and interfaces, and how a bike and a van can both deliver.
:::
