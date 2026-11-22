:::step{type=story title="What makes a program a real tool?"}
`git`, `docker`, `go` itself: the tools developers use every day are command-line programs. You type a name, some
options and a file, and they do one job well, with clear messages when something is wrong. A huge number of them are
written in Go, because Go builds a single file that runs anywhere, with nothing else to install.

Today Parcel's depot gets its first real tool: it reads a month of the depot's spending from a CSV file and prints the
biggest categories. Along the way you will discover why `-top 2` must come **before** the file name, and why
`go run` tells you one exit code while the terminal says another.

:::mission
Write `ReadTotals`, which adds up a messy CSV per category, and the `summary` tool, which prints the top categories with
a `-top` flag and a friendly message for a missing file.
:::
:::

:::step{type=try title="Read a file, line by line" file="15-files-and-cli/readfile.go" line="12-31"}
Open `readfile.go`:

```go
f, err := os.Open("expenses.csv")
if err != nil {
	fmt.Println("could not open:", err)
	return
}
defer f.Close()

scanner := bufio.NewScanner(f)
for scanner.Scan() {
	n++
	...
}
```

```bash run
cd /workspace/15-files-and-cli && go run readfile.go
```

```text
1 date,category,amount
2 2026-03-01,rent,18000
3 2026-03-01,fun,600
46 lines
open nope.csv: no such file or directory
```

- `os.Open` opens a file and, Go style, gives back the file **and** an error (chapter 7).
- `defer f.Close()` (chapter 13) closes it whatever happens, written right where it was opened.
- `bufio.Scanner` reads one line at a time, so even a huge file never has to fit in memory. `scanner.Text()` is the
  line, without its new-line character.
- A missing file is an ordinary error, whose message names the file.
:::

:::step{type=concept title="CSV: one record per line"}
`expenses.csv` has a header, then one purchase per line: date, category, amount. It is real, which means it is messy:
a blank line, an amount that says `abc`, a row with no category.

```text
date,category,amount
2026-03-01,rent,18000
2026-03-07,food,
```

`strings.Split(line, ",")` cuts a row into its pieces (keep only rows with exactly 3), and
`strconv.ParseFloat(amount, 64)` reads `210.5` or refuses `abc` with an error. Go also has a full CSV reader,
`encoding/csv`, which understands quoted commas too.

To tell "missing file" from other problems, check the error: `errors.Is(err, fs.ErrNotExist)` (chapter 13's
`errors.Is`, and the `io/fs` package).

:::picture{name="file-lines"}
A file is a ribbon of lines: the header first, then one record on each line.
:::
:::

:::step{type=task task=read_totals title="Your turn: totals from a messy CSV"}
Open `expenses.go` and make `ReadTotals(path)` give back a map of each category to its total. Skip the header, blank
lines, rows without three pieces or with no category, and amounts that are not numbers. A missing file returns the
error from opening it.

On `expenses.csv`, `rent` is `18000`.

```bash run
cd /workspace/15-files-and-cli && go run run.go
```

Then press **Check**.
:::

:::step{type=try title="Arguments and flags" file="15-files-and-cli/args.go" line="12-21"}
Open `args.go`. It prints what the program was given:

```bash run
cd /workspace/15-files-and-cli && go run args.go -top 2 expenses.csv
```

```text
4 [-top 2 expenses.csv]
top: 2 files: [expenses.csv]
```

`os.Args` holds every word, and `os.Args[0]` is the program itself. The `flag` package reads options for you:
`flag.Int("top", 3, "...")` declares `-top` with a default of 3, `flag.Parse()` reads them, and `flag.Args()` is what
is left over: the file names. Now put the file **first**:

```bash run
cd /workspace/15-files-and-cli && go run args.go expenses.csv -top 2
```

```text
4 [expenses.csv -top 2]
top: 3 files: [expenses.csv -top 2]
```

`flag` stops at the first word that is not a flag, so `-top 2` became two more file names and `top` stayed 3.
Options before arguments, always.
:::

:::step{type=concept title="Errors to stderr, and exit codes"}
Run it with no file, and ask the terminal how it ended:

```bash run
cd /workspace/15-files-and-cli && go run args.go; echo "exit $?"
```

```text
1 []
top: 3 files: []
usage: go run args.go [-top N] <file.csv>
exit status 2
exit 1
```

- `fmt.Fprintln(os.Stderr, ...)` writes to **standard error**: problems go there, so they stay on screen even when
  the normal output is saved to a file.
- `os.Exit(2)` ends the program with **exit code** 2. Scripts read it: 0 means success, anything else failure.
- And the curious last two lines: `go run` noticed your program's exit code 2 (`exit status 2`), then itself exited
  with 1. A program built with `go build` would give exactly 2.
:::

:::step{type=predict title="Guess first"}
:::question
`go run tool.go data.csv -verbose`. Does `flag` see `-verbose`?
:::
- [ ] Yes
- [x] No: it stops at `data.csv`, the first word that is not a flag
:::explain
Put flags before the file names: `go run tool.go -verbose data.csv`.
:::
:::

:::step{type=task task=summary_cli title="Your turn: the summary tool"}
Open `summary/main.go`, a program of its own in a sub-folder, and make it a real tool:

- `-top N` chooses how many categories to print (default 3), and the CSV file comes after it;
- print the categories with the biggest totals first, one per line, as `category: amount` with two decimals;
- for a missing file, print `File not found: <the path>` to standard error (no panic, no stack trace) and exit with
  code 1.

```bash run
cd /workspace/15-files-and-cli && go run ./summary -top 2 expenses.csv
```

Then try `go run ./summary nope.csv`, and press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
Why write `defer f.Close()` right after opening a file?
:::
- [x] So it is closed however the function ends, and never forgotten
- [ ] Because Go requires it
:::explain
`defer` runs on every way out: normal returns, early returns and panics.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
What is `os.Args[0]`?
:::
- [ ] The first word the user typed
- [x] The program itself
:::explain
The user's words start at `os.Args[1]`. With flags, use `flag.Args()`.
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
How do you check that an error means "the file does not exist"?
:::
- [ ] `err == "no such file"`
- [x] `errors.Is(err, fs.ErrNotExist)`
:::explain
The error from `os.Open` wraps `fs.ErrNotExist`, and `errors.Is` finds it (chapter 13).
:::
:::

:::step{type=deep-dive title="Go deeper: go build, cross-compiling and os.ReadFile"}
**go build.** `go build -o summary ./summary` leaves a single program file you can copy to any Linux machine and run,
with nothing else installed.

**Cross-compiling.** `GOOS=windows GOARCH=amd64 go build ./summary` builds a Windows `.exe` from Linux, in seconds.
This is a big reason so many tools are written in Go.

**os.ReadFile.** For small files, `data, err := os.ReadFile(path)` reads everything at once.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Open and read a file line by line with `os.Open`, `bufio.Scanner` and `defer f.Close()`.
- Parse messy CSV rows and tell a missing file apart with `errors.Is(err, fs.ErrNotExist)`.
- Read arguments and flags with `os.Args` and the `flag` package, flags first.
- Write a real tool: problems to `os.Stderr`, and a meaningful exit code with `os.Exit`.

:::photo{src="/lesson-images/go/go-15-notes.webp" alt="Handwritten notes about files and command-line tools in Go: os.Open then defer Close, bufio.Scanner reads line by line, errors.Is with fs.ErrNotExist, flag.Int for options, flags before file names, errors to os.Stderr, os.Exit with a code" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 16: goroutines and channels, the reason Go was created.
:::
