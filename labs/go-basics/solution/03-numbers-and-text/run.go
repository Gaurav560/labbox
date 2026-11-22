//go:build ignore

// Chapter 3: run it with: go run run.go
package main

import (
	"fmt"

	numbers "labbox/lab/03-numbers-and-text"
)

func main() {
	fmt.Println(numbers.Percent(45, 50), numbers.Percent(1, 3), numbers.Percent(7, 0))
	fmt.Println(numbers.FormatRupees(1250), numbers.FormatRupees(5))
}
