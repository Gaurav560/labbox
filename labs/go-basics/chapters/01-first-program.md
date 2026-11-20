:::step{type=story title="Why Go"}
Go was built at Google for programs that must be simple to read, quick to build and fast to run:
web servers, command-line tools, cloud systems like Docker and Kubernetes. It has few features on
purpose, so one Go program reads much like another.

:::mission
In `hello/hello.go`, write two small functions: one builds a greeting, and one turns hours and
minutes into minutes. Real tests check each one.
:::
:::

:::step{type=history title="The story of Go"}
Go powers much of the cloud you use every day. It was designed at Google by three engineers who were
tired of waiting.

:::before{title="Before Go"}
In 2007, Google's big servers were written in **C++** and **Java**. Builds of large C++ programs could
take most of an hour, and the languages had grown complicated. Using many CPU cores safely, with
threads and locks, was hard and full of subtle bugs. Every new engineer spent weeks just learning
the codebase's corners.
:::

:::solved
A small, simple language that **compiles in seconds**, makes **concurrency easy** (goroutines and
channels), and reads the same in every codebase, so large teams can work on large programs without
tripping over each other.
:::

Go was designed by **Robert Griesemer**, **Rob Pike** and **Ken Thompson** (who earlier co-created Unix
and the B language that led to C). It is maintained by the **Go team at Google** together with a large
open-source community.

:::timeline
- **2007** Griesemer, Pike and Thompson start sketching Go at Google.
- **2009** Go is announced as open source.
- **2012** Go 1.0, with a promise that code written for Go 1 keeps working.
- **2015** Go's compiler is rewritten in Go itself.
- **2022** Go 1.18 adds generics, after more than a decade of careful design.
:::

:::usedby{title="Industries"}
- Cloud infrastructure
- DevOps tools
- Backend APIs
- Networking
- Command-line tools
- Fintech
:::

:::usedby{title="Built with Go"}
- Docker
- Kubernetes
- Terraform
- Prometheus
- Uber
- Cloudflare
:::

:::funfact
Go's mascot, the gopher, was drawn by the artist **Renée French**. And Go has only **one** loop
keyword, `for`: there is no `while`, because `for` can do both.
:::
:::

:::step{type=concept title="A Go program"}
Every Go file starts with its **package**. A program starts in `func main` of package `main`:

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello, Go!")
}
```

A function names its inputs **with their types**, then the type it returns:

```go
func double(x int) int {
	return x * 2
}
```

Go is **statically typed**: the compiler checks every type before the program runs.
:::

:::step{type=example title="Worked example: a function that builds text"}
A complete Go function, line by line:

```go
func Welcome(city string) string {
	return "Welcome to " + city + "!"
}

// Welcome("Pune") is "Welcome to Pune!"
```

1. `func Welcome` names the function; the capital W makes it usable from other packages.
2. `(city string)` is the input and its type; the `string` after the brackets is the result's type.
3. `+` joins strings, and `return` hands the result back.

`Greeting` has exactly this shape.
:::

:::step{type=predict title="Guess first"}
:::question
What happens when you run this?

```go
func main() {
	name := "Asha"
	age := 17
}
```
:::
- [ ] It runs and prints nothing
- [x] It does not compile: the variables are never used
- [ ] It prints `Asha 17`
- [ ] It runs, with a warning
:::explain
Go refuses to compile a program with **unused variables** (and unused imports). It feels strict at
first, but it keeps leftovers and typos out of real code. `:=` declares a variable and works out its
type from the value.
:::
:::

:::step{type=try title="Run Go"}
Write a tiny program and run it:

```bash run
cat > /tmp/hello.go <<'GO'
package main

import "fmt"

func main() {
	name := "Asha"
	fmt.Println("Hello,", name)
	fmt.Println(3 + 4, 10 * 60)
}
GO
go run /tmp/hello.go
```

`go run` compiles and runs in one step.
:::

:::step{type=task task=greeting title="A greeting"}
In `hello/hello.go`, make `Greeting(name string) string` return `"Hello, <name>!"`.

`Greeting("Asha")` returns `"Hello, Asha!"`. Mind the comma, the space and the exclamation mark.
:::

:::step{type=concept title="Variables and numbers"}
Two ways to make a variable:

```go
var total int = 0   // the long form, with the type
count := 3          // the short form inside functions
count = count + 1   // = changes an existing variable
```

`+ - * /` work as usual on numbers. Several parameters of the same type can share it:
`func add(a, b int) int`.
:::

:::step{type=task task=total_minutes title="Hours and minutes"}
In `hello/hello.go`, make `TotalMinutes(hours, minutes int) int` return the total in minutes.

`TotalMinutes(2, 15)` returns `135`, and `TotalMinutes(0, 45)` returns `45`.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What happens to a Go program with an unused import?
:::
- [ ] It runs normally
- [ ] It prints a warning and runs
- [x] It does not compile
- [ ] The import is removed automatically
:::explain
Unused imports and unused variables are compile errors in Go. It keeps code free of leftovers.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Which name can other packages use?
:::
- [ ] `greeting`
- [x] `Greeting`
- [ ] `_greeting`
- [ ] All of them
:::explain
Only names starting with a **capital letter** are exported from a package.
:::
:::

:::step{type=deep-dive title="Packages, modules and gofmt"}
A **package** is a folder of `.go` files that share one name; `hello/hello.go` is package `hello`.
A **module** is a whole project, named in `go.mod` (here `labbox/lab`), so other code imports this
package as `labbox/lab/hello`.

Names that start with a **capital letter** (`Greeting`) are visible outside the package; lower case
names stay private. That one rule replaces `public` and `private` keywords.

Go code has one official layout: `gofmt` formats it with tabs and fixed spacing, and every editor runs
it on save. Teams never argue about style, and every Go codebase looks familiar.
:::

:::step{type=recap}
- A Go file starts with `package`; programs start at `func main` in package `main`.
- Functions name each input with its type, and the type they return.
- `:=` declares and infers a type; unused variables and imports do not compile.
- Capitalised names are exported; `go run` builds and runs.
:::
