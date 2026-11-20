:::step{type=story title="Why goroutines"}
Go's most famous feature is how easily it does many things at once: fetch ten web pages at the same
time, handle thousands of connections, process files in parallel. A **goroutine** is a function
running alongside the rest of the program, and it costs almost nothing to start.

:::mission
In `concurrent/concurrent.go`, run slow fetches at the same time while keeping the results in order,
and count words from many goroutines without corrupting the counts.
:::
:::

:::step{type=concept title="go and WaitGroup"}
Put `go` in front of a function call and it runs concurrently:

```go
var wg sync.WaitGroup
for i := range 3 {
	wg.Add(1)
	go func() {
		defer wg.Done()
		fmt.Println("worker", i)
	}()
}
wg.Wait()    // wait until all three called Done
```

`main` does not wait for goroutines by itself: without `wg.Wait()` the program could end before they
run.

:::picture{name="two-cooks"}
More cooks, all at once: dinner is ready sooner.
:::
:::

:::step{type=example title="Worked example: square numbers in parallel, in order"}
Each goroutine writes only its own slot, so the order is kept:

```go
func Squares(nums []int) []int {
	out := make([]int, len(nums))
	var wg sync.WaitGroup
	for i, n := range nums {
		wg.Add(1)
		go func() {
			defer wg.Done()
			out[i] = n * n
		}()
	}
	wg.Wait()
	return out
}
```

1. Make the result slice first, one slot per input.
2. Start one goroutine per item; each writes `out[i]`, its own slot.
3. `wg.Wait()` waits for all of them before returning.

`FetchAll` is this with `fetch(item)` in place of `n * n`.
:::

:::step{type=predict title="Guess first"}
:::question
Five calls each take 200 ms. Run one after another they take 1 second. Started as five goroutines and
then waited for, about how long do they take?
:::
- [ ] 1 second
- [x] About 200 ms
- [ ] About 40 ms
- [ ] It depends on the number of CPUs, at least 1 second
:::explain
Goroutines **wait** at the same time, so five 200 ms waits overlap into roughly 200 ms in total. This
is why Go is so good at network work, which is mostly waiting.
:::
:::

:::step{type=try title="Sequential versus concurrent"}
:::diagram{name="goroutines"}
One after another, five waits add up; as goroutines, they overlap.
:::

```bash run
cat > /tmp/conc.go <<'GO'
package main

import (
	"fmt"
	"sync"
	"time"
)

func slow(i int) { time.Sleep(200 * time.Millisecond) }

func main() {
	start := time.Now()
	for i := range 5 {
		slow(i)
	}
	fmt.Println("one by one:", time.Since(start).Round(time.Millisecond))

	start = time.Now()
	var wg sync.WaitGroup
	for i := range 5 {
		wg.Add(1)
		go func() { defer wg.Done(); slow(i) }()
	}
	wg.Wait()
	fmt.Println("together:  ", time.Since(start).Round(time.Millisecond))
}
GO
go run /tmp/conc.go
```
:::

:::step{type=task task=fetch_all title="Fetch everything at once"}
`FetchAll` in `concurrent/concurrent.go` works, but calls `fetch` one item after another. Make it
call `fetch` for every item **at the same time**, and still return the results in the items' order.

With five fetches of 200 ms each, it must finish in well under a second, and
`FetchAll([]string{"a", "b"}, strings.ToUpper)` must still return `[A B]`.
:::

:::step{type=concept title="Sharing data safely"}
Two goroutines writing the same map at the same moment is a **data race**: Go may crash with
`concurrent map writes`, or counts can silently come out wrong. Two ways to stay safe:

```go
var mu sync.Mutex
mu.Lock()            // only one goroutine at a time past this line
counts[word]++
mu.Unlock()
```

or send results over a **channel** to one goroutine that owns the map:

```go
ch := make(chan string)
go func() { ch <- "hello" }()
word := <-ch         // receives "hello"
```
:::

:::step{type=task task=word_counts title="Count words from many goroutines"}
In `concurrent/concurrent.go`, make `CountWords(texts []string) map[string]int` count every word (in
lower case) across all the texts, using one goroutine per text, and return an empty map for no texts.
With 200 texts at once the counts must be exactly right, every time.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What happens if `main` returns while goroutines are still running?
:::
- [ ] It waits for them
- [x] They are stopped with the program
- [ ] They keep running
- [ ] It panics
:::explain
When `main` returns the whole program ends, goroutines included. That is why `wg.Wait()` matters.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Several goroutines add to one map. What keeps it safe?
:::
- [ ] Nothing is needed
- [x] A `sync.Mutex` around each write
- [ ] Making the map bigger
- [ ] `defer`
:::explain
Lock a mutex around each write (or send values over a channel to one owner). Unprotected map writes crash the program.
:::
:::

:::step{type=deep-dive title="Do not communicate by sharing memory"}
Go's motto is "do not communicate by sharing memory; share memory by communicating": instead of many
goroutines locking one map, pass values over channels to a goroutine that owns the data. Both styles
are fine; mutexes are simpler for a counter, channels for pipelines of work.

`go test -race` (and `go run -race`) finds data races while your code runs; it needs a C compiler,
which this lab machine leaves out to stay small. `context.Context` lets you cancel a whole group of
goroutines, for example when a web request is abandoned, and `errgroup` collects the first error from
a group. Goroutines start with a few kilobytes of stack, so a server running a hundred thousand of them
is normal.
:::

:::step{type=recap title="Course complete"}
- `go f()` runs `f` concurrently; a `sync.WaitGroup` waits for a group.
- Write each result to its own slot (or index) to keep the order.
- Protect shared maps with a `sync.Mutex`, or send values over channels.
- You have learned Go from the first line to goroutines: well done.
:::
