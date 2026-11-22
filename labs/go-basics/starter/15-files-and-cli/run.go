//go:build ignore

// Chapter 15: run it with: go run run.go
package main

import (
	"fmt"

	expenses "labbox/lab/15-files-and-cli"
)

func main() {
	totals, err := expenses.ReadTotals("expenses.csv")
	fmt.Println(totals["rent"], len(totals), err)
}
