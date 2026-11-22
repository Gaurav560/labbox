// Chapter 15: a command-line program. Run it with: go run ./summary -top 3 expenses.csv
package main

import (
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"sort"

	expenses "labbox/lab/15-files-and-cli"
)

func main() {
	top := flag.Int("top", 3, "how many categories to show")
	flag.Parse()
	path := flag.Arg(0)
	totals, err := expenses.ReadTotals(path)
	if errors.Is(err, fs.ErrNotExist) {
		fmt.Fprintf(os.Stderr, "File not found: %s\n", path)
		os.Exit(1)
	} else if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	names := make([]string, 0, len(totals))
	for k := range totals {
		names = append(names, k)
	}
	sort.Slice(names, func(i, j int) bool { return totals[names[i]] > totals[names[j]] })
	for i, name := range names {
		if i == *top {
			break
		}
		fmt.Printf("%s: %.2f\n", name, totals[name])
	}
}
