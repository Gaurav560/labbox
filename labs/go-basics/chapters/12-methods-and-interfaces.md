:::step{type=story title="How can a bike and a van share one loop?"}
Parcel's fleet has bikes and vans. A bike takes 4 minutes per kilometre; a van takes 2, plus 5 minutes per stop. One
loop has to ask every vehicle how long a delivery takes. A bike is not a van. So what type does the loop's variable
have?

Travellers meet the same problem at every border: different plugs everywhere. An adapter fits the wall socket on one
side and the device on the other, and neither needs to know about the other. Go interfaces work the same way.

:::photo{src="/lesson-images/go/travel-adapters.webp" alt="Travel plug adapters plugged into a power strip on a stone counter, charging cables leading away" credit="Grandmaster Huon" license="CC0" source="https://commons.wikimedia.org/wiki/File:Travel_adapters_in_action.jpeg"}
Travel adapters at work: anything with the right plug fits.
:::

Java would need `class Van implements Deliverer`, written into the van itself. Go does something quieter and, many say,
smarter: if a type **has the right methods**, it **is** a deliverer. No announcement needed. Today you meet methods,
and Go's interfaces, the idea the whole standard library is built on.

:::mission
Give rectangles and circles an `Area()` method, then add up the area of any mix of shapes.
:::
:::

:::step{type=try title="Two vehicles, one loop" file="12-methods-and-interfaces/deliver.go" line="8-23"}
Open `deliver.go`:

```go
type Deliverer interface {
	MinutesFor(km int) int
}

type Bike struct{}
type Van struct{ Stops int }

func (Bike) MinutesFor(km int) int  { return km * 4 }
func (v Van) MinutesFor(km int) int { return km*2 + v.Stops*5 }
```

```bash run
cd /workspace/12-methods-and-interfaces && go run deliver.go
```

```text
main.Bike: 40 minutes for 10 km
main.Van: 35 minutes for 10 km
```

- `func (v Van) MinutesFor(...)` is a **method**: a function attached to `Van`, with `v` as its receiver.
- `Deliverer` is an **interface**: a list of methods. Any type with a `MinutesFor(int) int` method is a `Deliverer`,
  automatically. Neither `Bike` nor `Van` mentions `Deliverer` anywhere.
- `[]Deliverer{Bike{}, Van{Stops: 3}}` holds both, and the loop calls each one's own version. `%T` printed the real
  type inside.
:::

:::step{type=concept title="Interfaces are satisfied implicitly"}
That quiet rule has a big consequence. Code written today can accept types written **next year, by someone else**,
without either knowing about the other. Go's standard library is full of tiny interfaces like this:

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
```

Files, network connections, compressed streams and strings all have a `Read` method, so one function that takes an
`io.Reader` works with all of them.

:::picture{name="plug-socket"}
Anything with the right plug fits the socket.
:::
:::

:::step{type=example title="Worked example: a square keeps the promise"}
```go
type Shape interface {
	Area() float64
}

type Square struct{ Side float64 }

func (s Square) Area() float64 {
	return s.Side * s.Side
}
```

1. `Square` has an `Area() float64` method, so it is a `Shape`. Nothing else to write.
2. Misspell the method as `Aera`, and `var s Shape = Square{2}` fails to compile:
   `Square does not implement Shape (missing method Area)`.
3. A value receiver is right here: computing an area changes nothing (chapter 11).
:::

:::step{type=task task=areas title="Your turn: areas"}
Open `shapes.go` and make the two `Area()` methods return the right areas: `Rect{W: 3, H: 4}.Area()` gives `12`, and
`Circle{R: 2}.Area()` gives about `12.566` (use `math.Pi`).

```bash run
cd /workspace/12-methods-and-interfaces && go run run.go
```

Then press **Check**.
:::

:::step{type=try title="Teach fmt how to print your type" file="12-methods-and-interfaces/stringer.go" line="8-21"}
One interface is everywhere: `fmt.Stringer`, which is just `String() string`. Open `stringer.go`:

```go
func (p Parcel) String() string {
	return fmt.Sprintf("parcel %s (%d kg)", p.ID, p.Weight)
}
```

```bash run
cd /workspace/12-methods-and-interfaces && go run stringer.go
```

```text
parcel P-101 (4 kg)
[parcel P-101 (4 kg) parcel P-102 (9 kg)]
```

`fmt.Println` checks whether a value has a `String()` method, and if it does, uses it. You never told `fmt` about
`Parcel`; `Parcel` just happens to fit the plug.
:::

:::step{type=predict title="Guess first"}
:::question
A type `Truck` has a method `MinutesFor(km int) int`. Is it a `Deliverer`?
:::
- [x] Yes, automatically
- [ ] Only if it says `implements Deliverer`
:::explain
Go interfaces are satisfied by having the methods. There is no `implements` keyword at all.
:::
:::

:::step{type=task task=total_area title="Your turn: the total area"}
In `shapes.go`, make `TotalArea(shapes)` add up the areas of any shapes, **rounded to 2 decimals**.

`TotalArea([]Shape{Rect{3, 4}, Circle{1}})` gives `15.14`, and `TotalArea(nil)` gives `0`.

```bash run
cd /workspace/12-methods-and-interfaces && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is a method in Go?
:::
- [ ] A function inside a class
- [x] A function with a receiver, attached to a type
:::explain
Go has no classes. `func (v Van) MinutesFor(...)` attaches the function to `Van`.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `fmt.Println(p)` use when `p` has a `String() string` method?
:::
- [x] The `String()` method
- [ ] The field values
:::explain
`fmt` checks for the `fmt.Stringer` interface and calls it.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why are small interfaces, like `io.Reader` with one method, so useful?
:::
- [ ] They are faster
- [x] Many different types can satisfy them, so one function works with all of them
:::explain
The fewer methods an interface asks for, the more types fit it.
:::
:::

:::step{type=deep-dive title="Go deeper: type switches, embedding and any"}
**Type switches.** `switch v := d.(type) { case Van: ...; case Bike: ... }` asks which concrete type is inside an
interface value.

**Embedding.** `type ExpressVan struct { Van }` gets all of `Van`'s methods for free: Go's answer to inheritance, by
composition.

**any.** `any` is the interface with no methods, which every type satisfies. `fmt.Println(a ...any)` accepts anything
because of it. Use it sparingly: you lose the compiler's help.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Write methods with value or pointer receivers.
- Define interfaces as lists of methods, satisfied implicitly by any type that has them.
- Put different types in one slice of an interface type, and let each answer in its own way.
- Make your types print nicely with a `String()` method.

:::photo{src="/lesson-images/go/go-12-notes.webp" alt="Handwritten notes about Go methods and interfaces: a method has a receiver, an interface is a list of methods, no implements keyword, have the methods and you fit, small interfaces fit many types, String method for printing" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 2. Parcel's data has shape now: slices, strings, maps, structs, pointers and interfaces. Next,
Part 3: real programs, starting with errors in depth.
:::
