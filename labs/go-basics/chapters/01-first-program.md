:::step{type=story title="Why Go"}
Go was built at Google for programs that must be simple to read, quick to build and fast to run:
web servers, command-line tools, cloud systems like Docker and Kubernetes. It has few features on
purpose, so one Go program reads much like another.

:::mission
In `hello/hello.go`, write two small functions: one builds a greeting, and one turns hours and
minutes into minutes. Real tests check each one.
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
