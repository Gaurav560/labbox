:::step{type=story title="Can one program do three things at once?"}
Parcel has three vans out, each taking 300 milliseconds to deliver. Do them one after another, and it takes 900. Do
them at the same time, and it takes 300.

Doing many things at once is the reason Go exists. Its designers worked on Google's servers, where every program
handles thousands of requests at the same moment, and the languages they had made that painful. So they built it into
Go itself, with one tiny keyword: `go`. Put it in front of a function call, and the call runs **alongside** everything
else, in a **goroutine**.

:::photo{src="/lesson-images/go/rob-pike.webp" alt="Rob Pike, one of the designers of Go: a man with short dark hair and rimless glasses, in a dark shirt" credit="Chlor at English Wikipedia" license="CC BY-SA 3.0" source="https://commons.wikimedia.org/wiki/File:Rob-pike_(cropped).jpg"}
Rob Pike, one of Go's three designers, who has spent decades on languages for doing many things at once.
:::

It sounds too easy, and it is: your first goroutines will vanish without a trace. Today you find out why, and learn
the two tools that make them reliable: **WaitGroups** and **channels**.

:::mission
Make `FetchAll` call every fetch at the same time while keeping the results in order, and make `CountWords` count
words with one goroutine per text, without crashing.
:::
:::

:::step{type=try title="Three deliveries that vanish" file="16-goroutines/forgot.go" line="16-21"}
Open `forgot.go`:

```go
for _, stop := range []string{"MG Road", "FC Road", "JM Road"} {
	go deliver(stop)
}
fmt.Println("all sent!")
```

```bash run
cd /workspace/16-goroutines && go run forgot.go
```

```text
all sent!
```

Not a single delivery printed. `go deliver(stop)` started three goroutines and **did not wait** for them. `main` went
straight on, printed `all sent!` and returned, and when `main` returns, the whole program ends, goroutines and all.
They were still sleeping on their way to MG Road.
:::

:::step{type=try title="Wait for them, and time it" file="16-goroutines/waitgroup.go" line="16-36"}
Open `waitgroup.go`:

```go
var wg sync.WaitGroup
for _, stop := range stops {
	wg.Add(1)
	go func() {
		defer wg.Done()
		deliver(stop)
	}()
}
wg.Wait()
```

```bash run
cd /workspace/16-goroutines && go run waitgroup.go
```

```text
one by one: 900ms
all at once: 300ms
```

A `sync.WaitGroup` is a counter: `Add(1)` before starting each goroutine, `Done()` (deferred, chapter 13) when it
finishes, and `Wait()` blocks until the counter is back to zero. Three deliveries in the time of one.

`go func() { ... }()` starts an unnamed function as a goroutine, right there. Since Go 1.22, each lap of the loop gets
its own `stop`, so every goroutine delivers to the right address.
:::

:::step{type=concept title="Channels: goroutines talk"}
A **channel** is a pipe between goroutines. One sends, another receives:

```go
results := make(chan string)
go func() { results <- "P-1 weighs 4 kg" }()   // send
msg := <-results                                // receive: waits until something arrives
```

Receiving **waits**, which is how goroutines hand work back without any shared variables. Go's motto, from Rob Pike:
"Do not communicate by sharing memory; instead, share memory by communicating."

:::diagram{name="go-channels"}
Three goroutines send into one channel, and main receives the results in the order they finish.
:::
:::

:::step{type=try title="Results come back in any order" file="16-goroutines/channel.go" line="12-20"}
Open `channel.go`: three goroutines each send one result.

```bash run
cd /workspace/16-goroutines && go run channel.go
```

```text
P-3 weighs 7 kg
P-1 weighs 4 kg
P-2 weighs 12 kg
```

Your order may differ: results arrive in the order the goroutines **finish**, not the order they started. When the
order matters, as in your next task, each goroutine must write to its **own** place: for example, `results[i]` of a
slice, where `i` is its position.
:::

:::step{type=example title="Worked example: weigh every parcel at once"}
```go
func WeighAll(parcels []string, weigh func(string) int) []int {
	weights := make([]int, len(parcels))
	var wg sync.WaitGroup
	for i, p := range parcels {
		wg.Add(1)
		go func() {
			defer wg.Done()
			weights[i] = weigh(p)
		}()
	}
	wg.Wait()
	return weights
}
```

1. Make the result slice first, the right length.
2. Each goroutine writes only to **its own slot**, `weights[i]`, so the order is kept and no two goroutines touch the
   same place.
3. `wg.Wait()` before returning, or you would return half-empty results.
:::

:::step{type=task task=fetch_all title="Your turn: fetch everything at once"}
Open `concurrent.go`. `FetchAll(items, fetch)` works, but calls `fetch` for one item after another. Make it call every
fetch **at the same time**, and still return the results in the items' order.

```bash run
cd /workspace/16-goroutines && go run run.go
```

Then press **Check**: it measures whether the fetches really overlap.
:::

:::step{type=try title="Many goroutines, one map" file="16-goroutines/race.go" line="11-25"}
Now the danger. Open `race.go`: 50 goroutines each add 1000 to the same map entry.

```bash run
cd /workspace/16-goroutines && go run race.go
```

```text
fatal error: concurrent map writes

goroutine 28 [running]:
internal/runtime/maps.fatal({0x49dfd4?, 0x553238?})
	/opt/go/src/runtime/panic.go:1197 +0x18
main.main.func1()
	/workspace/16-goroutines/race.go:19 +0x6c
created by main.main in goroutine 1
```

Go caught two goroutines writing the map at the same instant and stopped the program, on purpose, rather than let it
quietly corrupt your data. (On a lucky run it may survive and print a wrong total.) Shared data needs a guard: a
`sync.Mutex`, which only one goroutine can hold at a time.

```go
var mu sync.Mutex
mu.Lock()
counts["parcels"]++
mu.Unlock()
```
:::

:::step{type=predict title="Guess first"}
:::question
`main` starts five goroutines with `go work()` and returns at once. How many finish their work?
:::
- [ ] All five
- [x] Probably none: the program ends when `main` returns
:::explain
Nothing waits for them. Use a `sync.WaitGroup` and call `Wait()` before `main` ends.
:::
:::

:::step{type=task task=word_counts title="Your turn: count words in parallel"}
In `concurrent.go`, make `CountWords(texts)` count every word, in lower case, across all the texts, with **one
goroutine per text**. All of them add to one shared map, so protect it with a `sync.Mutex`.

```bash run
cd /workspace/16-goroutines && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What does `wg.Wait()` do?
:::
- [x] Blocks until every `Done` has balanced every `Add`
- [ ] Waits one second
- [ ] Starts the goroutines
:::explain
A WaitGroup is a counter; `Wait` blocks until it is back to zero.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What does `msg := <-results` do when nothing has been sent yet?
:::
- [ ] Gives an empty string
- [x] Waits until a value arrives
:::explain
Receiving from a channel blocks until another goroutine sends.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How do you keep results in order when many goroutines finish in any order?
:::
- [x] Each goroutine writes to its own slot, like `results[i]`
- [ ] Sort them afterwards
- [ ] Goroutines always finish in order
:::explain
Writing to its own index keeps the order and means no two goroutines share a slot.
:::
:::

:::step{type=deep-dive title="Go deeper: buffered channels, select and the race detector"}
**Buffered channels.** `make(chan string, 10)` can hold 10 values before a sender has to wait.

**select.** `select { case r := <-results: ...; case <-time.After(time.Second): ... }` waits for whichever comes
first: the classic way to give up after a timeout.

**The race detector.** `go run -race` watches every memory access and reports two goroutines touching the same data
without a guard, even when the program happens to survive.

**Why so cheap.** A goroutine starts with a few kilobytes of memory, so one program can run hundreds of thousands of
them. Go's scheduler spreads them across your computer's cores.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Start goroutines with `go`, and explain why they vanish when `main` returns.
- Wait for them with a `sync.WaitGroup`: `Add`, `defer Done`, `Wait`.
- Send and receive through channels, knowing results arrive in the order goroutines finish.
- Keep results in order with one slot per goroutine, and guard shared maps with a `sync.Mutex`.

:::photo{src="/lesson-images/go/go-16-notes.webp" alt="Handwritten notes about goroutines: go starts a goroutine, main returning ends everything, WaitGroup Add Done Wait, channels send and receive, results arrive in finish order, one slot each keeps order, Mutex guards a shared map" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 17: tests with `go test`, the testing tool built into Go itself.
:::
