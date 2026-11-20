:::step{type=story title="Why methods and interfaces"}
Go has no classes, yet large Go programs are well organised. Two ideas do the work: **methods**,
functions attached to a type, and **interfaces**, which say what a value can do instead of what it is.

:::mission
In `shapes/shapes.go`, give rectangles and circles an `Area` method, then add up the area of any mix
of shapes through one interface.
:::
:::

:::step{type=concept title="Methods"}
A method is a function with a **receiver**, written before its name:

```go
type Rect struct {
	W, H float64
}

func (r Rect) Area() float64 {
	return r.W * r.H
}

room := Rect{W: 3, H: 4}
room.Area()    // 12
```
:::

:::step{type=predict title="Guess first"}
:::question
`Shape` is `interface { Area() float64 }`. Which line does **not** compile?

```go
var s Shape
s = Rect{W: 3, H: 4}     // Rect has Area()
s = Circle{R: 1}         // Circle has Area()
s = 42                   // ?
```
:::
- [ ] `s = Rect{...}`
- [ ] `s = Circle{...}`
- [x] `s = 42`
- [ ] All of them compile
:::explain
A type satisfies an interface just by **having its methods**; nothing needs to say "implements". `int`
has no `Area()` method, so `42` is not a `Shape`, and the compiler catches it.
:::
:::

:::step{type=try title="One interface, many types"}
```bash run
cat > /tmp/sh.go <<'GO'
package main

import "fmt"

type Sayer interface{ Say() string }
type Dog struct{}
type Robot struct{ ID int }

func (Dog) Say() string     { return "woof" }
func (r Robot) Say() string { return fmt.Sprint("beep ", r.ID) }

func main() {
	for _, s := range []Sayer{Dog{}, Robot{7}} {
		fmt.Println(s.Say())
	}
}
GO
go run /tmp/sh.go
```
:::

:::step{type=task task=areas title="Areas"}
In `shapes/shapes.go`, make the two `Area()` methods return the right areas:

- `Rect{W: 3, H: 4}.Area()` returns `12`
- `Circle{R: 2}.Area()` returns `4π` (about 12.566): use `math.Pi`
:::

:::step{type=concept title="Code that works with any Shape"}
A function that takes an interface works for every type that has the methods, including types written
later by someone else:

```go
func Describe(s Shape) string {
	return fmt.Sprintf("area %.1f", s.Area())
}
```

That is Go's answer to inheritance: small interfaces, satisfied implicitly.
:::

:::step{type=task task=total_area title="The total area"}
In `shapes/shapes.go`, make `TotalArea(shapes []Shape) float64` add up the areas, **rounded to 2
decimals**.

- `TotalArea([]Shape{Rect{3, 4}, Circle{1}})` returns `15.14`
- `TotalArea(nil)` returns `0`
:::

:::step{type=deep-dive title="Small interfaces"}
The best Go interfaces have one or two methods. `io.Reader` has just `Read(p []byte) (int, error)`, and
because files, network connections, buffers and HTTP bodies all have it, one function that takes an
`io.Reader` works with all of them.

Define interfaces where they are **used**, not where types are made: a function asks only for the
methods it needs. And the empty interface `any` (`interface{}`) accepts every value, at the cost of
checking its type at run time, so use it sparingly.
:::

:::step{type=recap}
- A method is a function with a receiver: `func (r Rect) Area() float64`.
- An interface lists methods; any type with them satisfies it, implicitly.
- Functions that take interfaces work for types written later.
- Keep interfaces small and define them where they are used.
:::
