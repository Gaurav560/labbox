:::step{type=story title="Can you turn a messy month into one clear answer?"}
Parcel is a real company now, with depots in Pune, Mumbai and Delhi. Every delivery ends up as a line in
`deliveries.csv`: the parcel, its depot, its weight and how many minutes it took. At the end of each month, someone has
to answer simple questions: how much did we deliver, how fast, from which depot, and which lines in the file are
broken?

The developer who started the report left before finishing it. You have the file, a half-written `report.go`, and
everything from the last seventeen chapters: files, structs, maps, errors, a fair tie rule and a plan. This is exactly
the kind of job a new Go developer is given in their first week.

:::mission
Write `DepotReport`, which reads the month's deliveries into one `Report`, and `BusiestDepot`, which names the depot
that shipped the most, fairly.
:::
:::

:::step{type=try title="Size up the data first"}
Before writing code against a file, look at it. Two classic terminal tools help:

```bash run
cd /workspace/18-capstone && wc -l deliveries.csv && cut -d, -f2 deliveries.csv | sort | uniq -c | sort -rn
```

```text
12 deliveries.csv
      4 Pune
      3 Mumbai
      2 Delhi
      2 
      1 depot
```

12 lines. `cut -d, -f2` takes the second column, the depot, and `uniq -c` counts each one. The two blank depots are one
blank line and one row with no depot; `depot` is the header. Open the file, and you will also find a weight of `abc`
and a row with no minutes.
:::

:::step{type=concept title="A plan before code" file="18-capstone/report.go" line="4-11"}
Open `report.go`. The result is already designed for you, as a struct:

```go
type Report struct {
	Delivered int            // how many good rows
	TotalKg   int            // their total weight
	AvgMins   float64        // their average delivery time, rounded to 1 decimal; 0 when there are none
	PerDepot  map[string]int // kilograms per depot
	BadLines  []int          // line numbers (the header is line 1) of rows that cannot be used
}
```

This is the biggest function in the course, and that is exactly when to stop and plan, in plain words, before any code:

1. Open the file (chapter 15) and read it line by line, counting line numbers as you go.
2. Skip the header and blank lines. Split each other line into its four parts (chapter 8).
3. A row is **bad** when it has no depot, or a weight or minutes that `strconv.Atoi` refuses (chapter 7). Note its
   line number and move on.
4. For a good row: count it, add its weight and minutes, and add its weight to its depot (chapter 10).
5. At the end, the average (0 when nothing was delivered, chapter 3's guard), rounded to one decimal.

Every step is a chapter you have done. The only new trick is keeping the line numbers.
:::

:::step{type=example title="Worked example: rows with their line numbers"}
```go
scanner := bufio.NewScanner(f)
line := 0
for scanner.Scan() {
	line++
	text := strings.TrimSpace(scanner.Text())
	if line == 1 || text == "" {
		continue
	}
	fmt.Println(line, text)
}
```

Count **every** line, blank ones included, before deciding to skip it, so the number always matches what someone sees
in an editor.

:::trace{title="four lines of a file"}
| line | text | prints | note |
|---|---|---|---|
| 1 | id,depot,weight_kg,minutes | (nothing) | The header is line 1, not data. |
| 2 | P-101,Pune,4,35 | 2 P-101,Pune,4,35 | The first real row. |
| 3 | (blank) | (nothing) | Blank: skipped, but it still counts. |
| 4 | P-104,Mumbai,abc,25 | 4 P-104,Mumbai,abc,25 | So this row is line 4, as an editor shows it. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
Which of these rows are **bad lines** for the report?

```text
id,depot,weight_kg,minutes
P-1,Pune,4,30
P-2,,3,20
P-3,Goa,x,10
P-4,Goa,6,50
```
:::
- [ ] Only line 4 (`x`)
- [x] Lines 3 and 4
- [ ] Lines 1, 3 and 4
:::explain
Line 3 has no depot and line 4 has no number for its weight, so neither can go in the report. The header is not data,
so it is never a bad line.
:::
:::

:::step{type=task task=depot_report title="Your turn: the depot report"}
In `report.go`, finish `DepotReport(path)`. For the five lines in "Guess first", it gives 2 delivered, 10 kg, an
average of 40.0 minutes, `PerDepot` of `map[Goa:6 Pune:4]` and bad lines `[3 4]`.

Two more rules: a file with only the header gives an **empty** map and slice, never `nil` (chapter 7), and a missing
file returns the error from `os.Open`.

```bash run
cd /workspace/18-capstone && go run run.go
```

```text
7 delivered, 48 kg, 40.7 min on average <nil>
map[Delhi:9 Mumbai:13 Pune:26] busiest: Pune
bad lines: [6 7 10]
```

(Before `BusiestDepot` works, the second line ends in `busiest:` with nothing after it.) Then press **Check**.
:::

:::step{type=task task=busiest_depot title="Your turn: the busiest depot, fairly"}
In `report.go`, make `BusiestDepot(r)` return the depot with the most kilograms. On a tie, the name that sorts first
wins; with no depots at all, `""`.

Remember chapter 10: map order is random, so without a tie rule two depots with the same weight could swap places from
run to run. The check calls it 20 times per case.

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
A blank line sits at line 3 of the file. What number does the row after it get?
:::
- [ ] 3
- [x] 4
:::explain
Blank lines are skipped, not reported, but they still count, so the number matches what an editor shows.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Nothing was delivered. What should `AvgMins` be?
:::
- [x] `0`
- [ ] `NaN`, from 0 divided by 0
:::explain
Dividing a float by zero gives NaN in Go. Check the count first, as in chapter 3.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
Why return `[]int{}` rather than `nil` for "no bad lines"?
:::
- [ ] `nil` does not compile
- [x] An empty slice says "none" clearly, and encodes to JSON as `[]`, not `null`
:::explain
Both have length 0, but callers and other systems (chapter 14's JSON) treat them differently.
:::
:::

:::step{type=deep-dive title="Go deeper: where Go goes from here"}
You now know the Go that real programs are made of. The natural next steps:

- **Web servers.** `net/http` in the standard library is a production web server: `http.HandleFunc("/parcels", ...)`
  and `http.ListenAndServe(":8080", nil)`, with chapter 14's JSON and chapter 16's goroutines (one per request,
  automatically).
- **context.** The `context` package carries deadlines and cancellation through goroutines, so a slow request can be
  stopped cleanly.
- **Generics.** `func Max[T int | float64](xs []T) T` writes one function for many types, Go 1.18's biggest addition.

Docker, Kubernetes and much of the cloud's machinery are written in exactly this language, by people who started where
you started: with `go run`.
:::

:::step{type=recap title="Course complete"}
You can now:

- Size up a data file before coding, and plan a big function in plain words first.
- Keep line numbers while reading a file, and report broken rows instead of hiding them.
- Combine files, structs, maps, errors and a fair tie rule into one real program.
- Write Go from your first `go run` to packages, JSON, command-line tools, goroutines and tests.

:::photo{src="/lesson-images/go/go-18-notes.webp" alt="Handwritten notes for the Go capstone: look at the data first, a plan in words, count every line even blank ones, report the bad lines, empty not nil, a tie rule makes it fair, Go from zero complete" ai="true"}
One page of notes for this chapter.
:::

That is Go from zero, all eighteen chapters. Parcel started as two `fmt.Println` lines; it ends as a tested tool that
reads real files and does many things at once. Well done.
:::
