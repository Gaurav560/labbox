:::step{type=story title="Why pointers"}
When you pass a value to a Go function, the function gets a **copy**. That keeps code safe and simple,
until you actually want the function to change the caller's value. Pointers are how you say "work on
the original".

:::mission
In `wallet/wallet.go`, fix a `Deposit` method that never changes the balance, and write `Swap`, which
exchanges two variables through pointers.
:::
:::

:::step{type=concept title="Values and pointers"}
`&x` is the **address** of `x`; a variable holding an address is a pointer, and `*p` reads or writes
the value it points to:

```go
n := 10
p := &n       // p is a *int pointing at n
*p = 20       // changes n
fmt.Println(n) // 20
```

A function that takes a pointer can change the caller's variable:

```go
func reset(x *int) { *x = 0 }
reset(&n)     // n is now 0
```

:::picture{name="envelope-address"}
A pointer is an address: two envelopes, one house.
:::
:::

:::step{type=example title="Worked example: a counter that really counts"}
A method that changes its struct needs a pointer receiver:

```go
type Counter struct{ N int }

func (c *Counter) Inc() {
	c.N++
}

var c Counter
c.Inc()
c.Inc()
// c.N is 2
```

1. `(c *Counter)` receives a pointer, so `c.N++` changes the caller's counter.
2. Go takes the address for you: `c.Inc()` works on a plain variable.

`Deposit` needs exactly this change.

:::trace{title="two calls to c.Inc()"}
| line | c.N | note |
|---|---|---|
| var c Counter | 0 | A new Counter starts with N at 0. |
| c.Inc() | 1 | Inc gets a pointer to c, so c.N++ changes the real counter. |
| c.Inc() | 2 | The same counter again: now 2. A value receiver would have left it at 0. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`wallet.go` starts with this method. What does the last line print?

```go
func (w Wallet) Deposit(amount int) {
	w.Balance += amount
}

w := Wallet{Balance: 100}
w.Deposit(50)
fmt.Println(w.Balance)
```
:::
- [ ] `150`
- [x] `100`
- [ ] `50`
- [ ] It does not compile
:::explain
`(w Wallet)` is a **value receiver**: the method gets a copy of the wallet, adds 50 to the copy, and
the copy is thrown away when it returns. The caller's wallet still holds 100. A pointer receiver,
`(w *Wallet)`, works on the original.
:::
:::

:::step{type=try title="Watch the copy"}
:::diagram{name="value-vs-pointer"}
A value receiver changes a copy that is thrown away; a pointer receiver changes the caller's wallet.
:::

```bash run
cat > /tmp/wallet.go <<'GO'
package main

import "fmt"

type Wallet struct{ Balance int }

func (w Wallet) ByValue(n int)    { w.Balance += n }
func (w *Wallet) ByPointer(n int) { w.Balance += n }

func main() {
	w := Wallet{Balance: 100}
	w.ByValue(50)
	fmt.Println("after ByValue:", w.Balance)
	w.ByPointer(50)
	fmt.Println("after ByPointer:", w.Balance)
}
GO
go run /tmp/wallet.go
```
:::

:::step{type=task task=deposit title="Fix Deposit"}
In `wallet/wallet.go`, fix `Deposit` so that

```go
w := Wallet{Balance: 100}
w.Deposit(50)
w.Deposit(25)
```

leaves `w.Balance` at `175`. Change as little as possible.
:::

:::step{type=concept title="When to use a pointer receiver"}
Use a pointer receiver when a method **changes** the value, or when the struct is large and copying it
would be wasteful. Go calls pointer methods on ordinary variables for you: `w.Deposit(50)` becomes
`(&w).Deposit(50)` automatically.

Keep it consistent: if one method of a type needs a pointer receiver, give them all one.
:::

:::step{type=task task=swap title="Swap two values"}
In `wallet/wallet.go`, make `Swap(a, b *int)` exchange the two values:

```go
x, y := 1, 2
Swap(&x, &y)
// now x is 2 and y is 1
```

`Swap(&x, &x)` must leave `x` unchanged.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does `&x` give?
:::
- [ ] A copy of x
- [x] The address of x
- [ ] x's type
- [ ] x multiplied
:::explain
`&x` is the address of `x`, a pointer; `*p` reads or writes what a pointer points to.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why is returning `&Wallet{}` from a function safe in Go?
:::
- [ ] It is not safe
- [x] Escape analysis keeps it alive on the heap
- [ ] Go copies it
- [ ] Only in tests
:::explain
The compiler sees the value outlives the function and keeps it on the heap; the garbage collector frees it later.
:::
:::

:::step{type=deep-dive title="Escape analysis and nil"}
In Go you can safely return a pointer to a local variable: `return &Wallet{}`. The compiler's **escape
analysis** sees that the value outlives the function and puts it on the heap, where the garbage
collector will free it later. There is no pointer arithmetic, so pointers cannot wander into random
memory.

The zero value of a pointer is `nil`, and reading through a nil pointer panics. Slices, maps and
channels are already small references, so you rarely need a pointer to them; pass them as they are.
:::

:::step{type=recap}
- Go passes copies: a function changing a parameter changes its copy.
- `&x` takes an address; `*p` reads or writes through a pointer.
- Methods that change their struct need a pointer receiver `(w *Wallet)`.
- Returning `&T{}` is safe; reading through a `nil` pointer panics.
:::
