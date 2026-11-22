:::step{type=story title="What do you build while waiting 45 minutes for your code to compile?"}
In 2007, three engineers at Google were waiting. Their C++ program took so long to build that there was time for a
long conversation while it compiled. They used that time to sketch a new language: one that builds in seconds, reads
clearly, and makes it easy to do many things at once. Two years later they released it. Its name is **Go**.

Today Go runs a huge part of the internet's machinery: Docker, Kubernetes and countless servers are written in it. And
it has opinions. Go refuses to run a program with one unused variable in it. By the end of this chapter you will have
met that strictness, and seen why so many teams love it.

Your project for this course is **Parcel**, a small parcel tracker: parcels, weights, vans and deliveries. Today Parcel
says its very first words.

:::mission
Make Parcel introduce itself, then fix a program that Go refuses to run.
:::
:::

:::step{type=history title="The story of Go"}
Go was designed at Google by Robert Griesemer, **Rob Pike** and **Ken Thompson**. Ken Thompson had already created Unix
with Dennis Ritchie, decades earlier:

:::photo{src="/lesson-images/go/ken-thompson-dennis-ritchie.webp" alt="Ken Thompson, with glasses and a long beard, smiling next to Dennis Ritchie, who has a grey beard" credit="Unknown author" license="Public domain" source="https://commons.wikimedia.org/wiki/File:Ken_Thompson_and_Dennis_Ritchie--1973.jpg"}
Ken Thompson (left), co-creator of Unix and later of Go, with Dennis Ritchie, creator of the C language.
:::

And every Go programmer knows this little creature: the **Go Gopher**, drawn by Renee French, Go's mascot since the
start.

:::photo{src="/lesson-images/go/go-gopher.webp" alt="The Go Gopher: a round, light blue cartoon rodent with big round eyes and two front teeth, standing upright" credit="Renee French" license="CC BY 3.0" source="https://commons.wikimedia.org/wiki/File:Go_gopher_frontpage.png"}
The Go Gopher, by Renee French.
:::

:::timeline
- **2007** Griesemer, Pike and Thompson start sketching Go at Google.
- **2009** Go is announced as open source.
- **2012** Go 1.0, with a promise that code written for Go 1 keeps working.
- **2015** Go's compiler is rewritten in Go itself.
- **2022** Go 1.18 adds generics, after more than a decade of careful design.
:::
:::

:::step{type=try title="Run your first program" file="01-hello-go/first.go" line="4-13"}
Open `first.go`:

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello from Parcel!")
	fmt.Println("Today's van carries 3 parcels.")
	fmt.Println(3*4, "kilograms in all")
	fmt.Println("Done.")
}
```

- `package main` says "this is a program you can run", and `func main()` is where it starts.
- `import "fmt"` brings in Go's **format** package, which prints things. `fmt.Println` prints one line.

In the terminal below, type this and press Enter:

```bash run
cd /workspace/01-hello-go && go run first.go
```

```text
Hello from Parcel!
Today's van carries 3 parcels.
12 kilograms in all
Done.
```

`go run` compiled your file into a real program and ran it, in about a second. `3*4` is maths, so Go worked it out
first. (The `//go:build ignore` line at the top of the file just tells Go "this file is a separate little program";
you can leave it alone.)
:::

:::step{type=concept title="What go run does with your file"}
Typing `go run first.go` starts a two-stage journey. Press Play:

:::diagram{name="go-runs-a-file"}
Go checks the whole file, compiles it to machine code, then runs it; a check failure means nothing runs at all.
:::

1. **Before anything runs**, Go checks the whole file: grammar, names, types, and things you declared but never used.
   Any problem is a **compile error**, and not a single line runs.
2. **While it runs**, something can still go wrong, like asking for a parcel that is not there. Go stops with a
   **panic** at that line; the lines before it already ran.
:::

:::step{type=try title="A program that stops halfway" file="01-hello-go/crash.go" line="8-14"}
Open `crash.go`. No typo at all:

```go
parcels := []string{"Books", "Lamp"}
fmt.Println("Parcels:", len(parcels))
next := 5
fmt.Println("Next up:", parcels[next])
fmt.Println("This line never runs.")
```

```bash run
cd /workspace/01-hello-go && go run crash.go
```

```text
Parcels: 2
panic: runtime error: index out of range [5] with length 2

goroutine 1 [running]:
main.main()
	/workspace/01-hello-go/crash.go:12 +0x73
exit status 2
```

`Parcels: 2` printed, so line 10 ran. Then line 12 panicked: the list has 2 parcels, numbered 0 and 1, so there is no
parcel number 5. Read the panic like a detective: **what** went wrong (`index out of range [5] with length 2`, and
it even tells you the length), then **where** (`crash.go:12`). Chapter 6 reads the rest.
:::

:::step{type=example title="Worked example: Parcel counts down"}
```go
package main

import "fmt"

func main() {
	fmt.Println("Leaving the depot in...")
	fmt.Println(3)
	fmt.Println(2)
	fmt.Println(1)
	fmt.Println("Go!")
}
```

```text
Leaving the depot in...
3
2
1
Go!
```

1. Each `fmt.Println` prints **one line**, in the order the lines are written.
2. Text goes inside double quotes: `"Go!"`. Numbers do not need them.
3. No semicolons: Go adds them for you at the end of each line. Every Go file in the world is formatted the same way,
   by a tool called `gofmt`, so nobody argues about style.
:::

:::step{type=task task=hello_parcel title="Your turn: Parcel says hello" file="01-hello-go/parcel.go"}
Open `parcel.go` and make it print exactly these two lines:

```text
Hello! I am Parcel.
I will track your deliveries.
```

You will need `import "fmt"` near the top, just like `first.go`.

```bash run
cd /workspace/01-hello-go && go run parcel.go
```

When it prints those two lines, press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
A Go file declares a variable `count := 12` and never uses it. What happens with `go run`?
:::
- [ ] It runs, and ignores `count`
- [ ] It runs, with a warning
- [x] It refuses to run: a compile error
:::explain
Go treats unused variables and unused imports as errors. Unused things are usually mistakes, or leftovers that make
code harder to read, so Go stops you from keeping them.
:::
:::

:::step{type=try title="Go refuses to run this" file="01-hello-go/fixme.go" line="4-16"}
Open `fixme.go` and try to run it:

```bash run
cd /workspace/01-hello-go && go run fixme.go
```

```text
# command-line-arguments
./fixme.go:8:2: "strings" imported and not used
./fixme.go:12:2: declared and not used: count
```

Two errors, both reported at once, each with its **file:line:column**. Nothing ran. The program imports the
`strings` package and never uses it, and it makes a variable `count` and never uses it either. In most languages that
is fine. In Go, it is not allowed: every import and every variable must earn its place.
:::

:::step{type=task task=fix_first_errors title="Your turn: make Go happy" file="01-hello-go/fixme.go"}
Fix `fixme.go` so it runs. Remove the import nobody uses, and **use** `count` instead of the number 12 on the last
line. When it works it prints:

```text
Parcel is starting...
Ready to track your deliveries.
Parcels on the van: 12
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Which function does Go run first when a program starts?
:::
- [ ] The first function in the file
- [x] `main`, in `package main`
- [ ] `init`, always
:::explain
A runnable Go program is `package main` with a `func main()`. That is where it starts.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `./fixme.go:12:2` point at?
:::
- [x] File fixme.go, line 12, column 2
- [ ] Error number 12, version 2
- [ ] Line 2 of fixme.go
:::explain
Go always gives file, line and column, so you can jump straight to the spot.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
A program prints two lines, then panics at line 9. What happened?
:::
- [x] It compiled fine, ran, and line 9 went wrong while running
- [ ] Go found the mistake before running anything
:::explain
Output before the panic means the program compiled and started. Compile errors print nothing else.
:::
:::

:::step{type=deep-dive title="Go deeper: go build, gofmt and the Go Playground"}
**go build.** `go run` compiles to a temporary program and runs it. `go build first.go` leaves the program behind as a
file you can copy to another Linux machine and run, with nothing else installed. That single, self-contained file is a
big reason Go is loved for servers and tools.

**gofmt.** `gofmt -w first.go` rewrites your file in the one official style. VS Code runs it every time you save.

**The Go Playground.** go.dev/play runs Go in your browser: handy for trying one small idea.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Run a Go program with `go run file.go`, starting from `func main()` in `package main`.
- Print with `fmt.Println`, after `import "fmt"`.
- Explain that Go checks the whole file first, and refuses unused variables and imports.
- Read a compile error's file:line:column, and a panic's message and line.

:::photo{src="/lesson-images/go/go-01-notes.webp" alt="Handwritten notes about a first Go program: package main and func main, import fmt, go run file.go, Go checks everything first, unused import or variable means it will not run, a panic stops at the line" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 2: functions, and a Go trick most languages do not have: one function, two answers.
:::
