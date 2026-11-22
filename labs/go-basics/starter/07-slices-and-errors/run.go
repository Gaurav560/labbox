//go:build ignore

// Chapter 7: run it with: go run run.go
package main

import (
	"fmt"

	till "labbox/lab/07-slices-and-errors"
)

func main() {
	fmt.Println(till.Total([]int{1500, 2000}))
	fmt.Println(till.ParseAmount("12.50"))
	fmt.Println(till.ParseAmount("abc"))
}
