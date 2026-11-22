:::step{type=story title="A program that runs is not a program that is right"}
In 1947, the team running the Harvard Mark II computer found it giving wrong answers. Inside one of its relays they
found the cause: a real moth. They taped it into the logbook with the note "First actual case of bug being found."

:::photo{src="/lesson-images/python/first-computer-bug-1947.webp" alt="A page of the Harvard Mark II logbook from 9 September 1947, with a moth taped to it and the note First actual case of bug being found" credit="U.S. Naval History and Heritage Command" license="Public domain" source="https://commons.wikimedia.org/wiki/File:First_Computer_Bug,_1947.jpg"}
The real page, 9 September 1947: the moth is still taped to it.
:::

Go catches a lot before your program even starts: wrong types, missing arguments, unused variables. But no compiler
can catch this kind: Parcel's `TotalWeight` compiles perfectly, runs without a panic, and says a van carries 19 kg when
it carries 23. Today you learn to hunt both kinds: the loud ones that panic, and the quiet ones that just lie.

:::mission
Read a real Go panic, then use labelled prints and tiny test programs to find and fix two quiet bugs.
:::
:::

:::step{type=try title="A panic two functions deep" file="06-finding-bugs/report.go" line="8-25"}
Open `report.go`. It reports the heaviest parcel in each van:

```go
func heaviest(weights []int) int {
	best := weights[0]
	for _, w := range weights {
		if w > best {
			best = w
		}
	}
	return best
}

func summary(van string, weights []int) string {
	return fmt.Sprintf("%s: heaviest parcel %d kg", van, heaviest(weights))
}
```

```bash run
cd /workspace/06-finding-bugs && go run report.go
```

```text
Morning van: heaviest parcel 12 kg
panic: runtime error: index out of range [0] with length 0

goroutine 1 [running]:
main.heaviest(...)
	/workspace/06-finding-bugs/report.go:9
main.summary({0x49cd3b?, 0x207c52cb8030?}, {0x207c52d4ce70?, 0x1?, 0x1?})
	/workspace/06-finding-bugs/report.go:19 +0xb1
main.main()
	/workspace/06-finding-bugs/report.go:24 +0x9f
exit status 2
```

The morning van worked. The evening van, with no parcels at all, panicked. This is a **stack trace**: the list of
function calls that were waiting for an answer when things went wrong. (Your hex numbers will differ: they are memory
addresses.)
:::

:::step{type=concept title="Read a panic from the top"}
Press Play and read this one the way Go developers do:

:::diagram{name="go-panic-trace"}
The panic line says what went wrong; the first function listed is where; the ones below are how the program got there.
:::

Told in the order things happened: `main` (line 24) called `summary("Evening van", ...)`; `summary` (line 19) called
`heaviest` with an empty slice; and `heaviest` (line 9) asked for `weights[0]`, the first parcel of none.

The fix is a decision about empty vans. One `if` at the top of `heaviest`:

```go
if len(weights) == 0 {
	return 0
}
```

Try it and run the file again: `Evening van: heaviest parcel 0 kg`.
:::

:::step{type=try title="Now the quiet kind" file="06-finding-bugs/van.go" line="3-19"}
Open `van.go`. Its two functions belong to a package, so a tiny program, `ask.go`, calls them with small questions:

```bash run
cd /workspace/06-finding-bugs && go run ask.go
```

```text
19
0
true
```

No panic. But the van's parcels weigh 4 + 12 + 7 = **23** kg, not 19. A van with a single 4 kg parcel weighs **0**? And
`CanLoad(10, 10)` says `true`: a van already holding 10 parcels, with room for 10, can take one more? That breaks
Parcel's own rule. Nothing crashed, because nothing is wrong with the types. The logic is wrong.

`ask.go` is the Go way to "ask a function a question": Go has no interactive prompt like Python's or Node's, but a
five-line program and `go run` take two seconds. Small, sharp inputs, like a single parcel, make bugs obvious.
:::

:::step{type=example title="Worked example: make the invisible visible"}
A bug lives in values you cannot see: the variables inside a function while it runs. The simplest debugging tool in the
world is still a print: show what you want to see, run, compare with what you expected, then remove it.

Suppose you doubt the loop in `TotalWeight`. Add one line inside it:

```go
for i := 1; i < len(weights); i++ {
	fmt.Println("i =", i, "weight =", weights[i])
	total += weights[i]
}
```

With `[]int{4, 12, 7}`, it prints:

```text
i = 1 weight = 12
i = 2 weight = 7
```

Each line is one lap, and the laps show the answer: position 0, the 4 kg parcel, is never visited. Label your values
(`"i =", i`), or a screen full of bare numbers becomes a puzzle of its own. (Add `import "fmt"` while you debug, and
remove both afterwards: remember, Go refuses an unused import.)

For structs (chapter 10), `fmt.Printf("%+v\n", parcel)` prints every field with its name.
:::

:::step{type=predict title="Guess first"}
:::question
`TotalWeight` loops with `for i := 1; i < len(weights); i++`. For `[]int{4, 12, 7}`, which weights does it add?
:::
- [ ] 4, 12 and 7
- [x] 12 and 7
- [ ] 4 and 12
:::explain
`i` starts at 1, so position 0, the first parcel (4 kg), is never visited: 12 + 7 = 19.
:::
:::

:::step{type=task task=fix_total_weight title="Your turn: the total that forgets a parcel"}
Fix `TotalWeight` in `van.go`, so that `TotalWeight([]int{4, 12, 7})` gives `23`.

1. Prove it first with a labelled print inside the loop, and run `go run ask.go`. Which positions are visited?
2. Find what decides where the loop starts, and fix it.
3. Remove your print (and the `fmt` import), and run it again: `23`.

An empty van must still give `0`. Then press **Check**.
:::

:::step{type=task task=fix_can_load title="Your turn: a full van takes no more"}
Fix `CanLoad` in `van.go`. A van may take another parcel while it holds **fewer** parcels than its limit; at the limit,
no more:

- `CanLoad(9, 10)` gives `true` (room for one more),
- `CanLoad(10, 10)` gives `false` (full),
- `CanLoad(0, 0)` gives `false`.

1. Look inside: print `room` before the `return`, or add a line to `ask.go`.
2. What is `room` exactly at the limit? Is that enough room for another parcel?
3. Fix the comparison, remove your debugging line, and run `go run ask.go`.

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
In a Go panic, which function is listed first?
:::
- [x] The one where the panic happened
- [ ] `main`, always
- [ ] The first function in the file
:::explain
The newest call comes first. `main.main` is at the bottom, where everything began.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
A function compiles, runs and returns a wrong number. What helps first?
:::
- [ ] Reading the compile errors
- [x] Printing the values inside it, and trying tiny inputs
- [ ] Rewriting it from scratch
:::explain
There is no error to read. Make the hidden values visible, and test with inputs where you know the answer.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `index out of range [0] with length 0` tell you?
:::
- [x] The code asked for the first item of an empty slice
- [ ] The slice has one item
- [ ] Item 0 is empty
:::explain
Length 0 means nothing is in there, so even item 0 does not exist.
:::
:::

:::step{type=deep-dive title="Go deeper: Delve, go vet and recover"}
**Delve.** `dlv debug` is Go's real debugger: pause on any line and look at every variable. VS Code's Go extension uses
it when you click next to a line number.

**go vet.** `go vet ./...` finds suspicious code that compiles but is probably wrong, like a `Printf` with the wrong
number of values. LabBox's checks run it before your tests.

**recover.** A deferred function can call `recover()` to catch a panic and carry on. Servers use it so one bad
request cannot crash the whole server. Most code should simply avoid panicking.

**Off-by-one.** Starting at 1 instead of 0, or `>=` instead of `>`: the same two mistakes, in every language, every
day. You have now fixed both.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Tell a compile error, a panic (a loud crash) and a logic bug (a quiet wrong answer) apart.
- Read a Go panic: what went wrong, then the functions, newest first, each with its file and line.
- Make hidden values visible with labelled prints, and `%+v` for structs.
- Ask functions small questions with a tiny `go run` program.

:::photo{src="/lesson-images/go/go-06-notes.webp" alt="Handwritten notes about finding bugs in Go: read the panic from the top, newest call first, label your prints, a tiny ask program instead of a REPL, remove the debug import, off by one" ai="true"}
One page of notes for this chapter.
:::

That is the end of Part 1. Parcel can talk, work things out, decide and loop, and you can fix it when it misbehaves.
Next, Part 2: working with data, starting with slices and errors.
:::
