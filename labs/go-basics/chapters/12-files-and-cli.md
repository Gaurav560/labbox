:::step{type=story title="Why files and command-line programs"}
Go is a favourite for command-line tools: one fast binary, nothing else to install. Most such tools
read a file, work out something, and print it, and they fail with one clear sentence when the input is
wrong.

:::mission
In `expenses/expenses.go`, read `expenses.csv` (a real, messy file in your workspace) into totals per
category, then finish `cmd/summary`, a program that prints the biggest categories.
:::
:::

:::step{type=concept title="Opening and reading files"}
```go
f, err := os.Open("expenses.csv")
if err != nil {
	return nil, err
}
defer f.Close()           // runs when the function returns, however it returns
```

`defer` is Go's way to make sure clean-up happens. For CSV, the `encoding/csv` package handles quoting
(`"snacks, tea"`) correctly:

```go
r := csv.NewReader(f)
row, err := r.Read()      // []string{"2026-03-02", "food", "120"}, or io.EOF at the end
```

:::picture{name="file-lines"}
Each line of a CSV file is one row, cut at the commas.
:::
:::

:::step{type=example title="Worked example: read a file line by line"}
Open, defer the close, and read:

```go
func CountLines(path string) (int, error) {
	f, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer f.Close()
	n := 0
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		n++
	}
	return n, sc.Err()
}
```

1. `os.Open` returns the file or an error; return the error for a missing file.
2. `defer f.Close()` runs when the function returns, however it returns.
3. Read in a loop until the reader says it is done.

`ReadTotals` is this shape with `csv.NewReader` in place of the scanner.

:::trace{title='CountLines("notes.txt") for a file with 3 lines'}
| step | n | note |
|---|---|---|
| os.Open | 0 | The file opened, so err is nil and we go on. defer schedules Close for later. |
| sc.Scan() reads line 1 | 1 | Scan returns true while there is a line to read. |
| sc.Scan() reads line 2 | 2 |  |
| sc.Scan() reads line 3 | 3 |  |
| sc.Scan() returns false | 3 | No more lines: the loop ends, Close runs, and the function returns 3, nil. |
:::
:::

:::step{type=predict title="Guess first"}
:::question
`expenses.csv` has a row `2026-03-07,food,` (no amount). What does `strconv.ParseFloat("", 64)` return?
:::
- [ ] `0, nil`
- [x] `0` and an error
- [ ] It panics
- [ ] `NaN, nil`
:::explain
An empty string is not a number, so `ParseFloat` returns an error, and you skip that row. Go never
guesses: bad input always comes back as an error you decide what to do with.
:::
:::

:::step{type=try title="Look at the real file"}
```bash run
head -5 expenses.csv; echo ...; grep -n -v -E '^[0-9-]+,[a-z]+,[0-9.]+$' expenses.csv
```

The second command lists the lines that do not look like `date,category,amount`. Your code must
survive all of them.
:::

:::step{type=task task=read_totals title="Totals from a CSV file"}
In `expenses/expenses.go`, make `ReadTotals(path string) (map[string]float64, error)` return the total
per category, rounded to 2 decimals. Skip the header, blank lines, and rows with a missing or
non-numeric amount. For a missing file, return an error for which `errors.Is(err, fs.ErrNotExist)` is
true (returning or wrapping `os.Open`'s error does that).

Set `r.FieldsPerRecord = -1` so a short row does not stop the reading.
:::

:::step{type=concept title="A command-line program"}
`cmd/summary/main.go` is package `main`. The `flag` package reads options:

```go
top := flag.Int("top", 3, "how many categories to show")
flag.Parse()
path := flag.Arg(0)          // the first argument that is not a flag
```

Errors for people go to `os.Stderr`, and `os.Exit(1)` tells the shell the program failed.
:::

:::step{type=task task=summary_cli title="The summary program"}
Finish `cmd/summary/main.go` so that

```text
$ go run ./cmd/summary -top 2 expenses.csv
rent: 18000.00
shopping: 4095.00
```

prints the biggest categories, biggest first, as `category: amount` with two decimals (3 when `-top`
is left out), and `go run ./cmd/summary missing.csv` prints `File not found: missing.csv` to stderr and
exits with code `1`, without a panic.
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
When does a deferred call run?
:::
- [ ] Immediately
- [x] When the function returns
- [ ] When the program ends
- [ ] Never, unless there is an error
:::explain
`defer` schedules the call for when the surrounding function returns, which makes clean-up impossible to forget.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Where should a command-line tool print an error for a person?
:::
- [ ] `os.Stdout`
- [x] `os.Stderr`
- [ ] A log file only
- [ ] Nowhere: just exit
:::explain
Errors go to stderr, so they still show when the normal output is sent to a file or another program.
:::
:::

:::step{type=deep-dive title="Single binaries and cross-compiling"}
`go build ./cmd/summary` produces one file with everything inside, the Go runtime included. Copy it to
a server and run it; nothing else is needed. Set two variables and Go builds for another system:
`GOOS=windows GOARCH=amd64 go build ./cmd/summary` makes a Windows `.exe` from Linux.

For big files, read line by line (`bufio.Scanner`, or `csv.Reader` in a loop as here) instead of
`os.ReadFile`, which loads everything into memory. Tools with many sub-commands (`git commit`,
`docker run`) are usually built with a library such as `cobra` on top of the same ideas.
:::

:::step{type=recap}
- `os.Open` plus `defer f.Close()`; `encoding/csv` handles quoted commas.
- Skip what you cannot read; return real errors (like a missing file) to the caller.
- `flag` reads options; `flag.Arg(0)` is the first plain argument.
- Errors for people go to `os.Stderr`; `os.Exit(1)` signals failure.
:::
