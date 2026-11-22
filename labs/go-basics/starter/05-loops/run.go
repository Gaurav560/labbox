//go:build ignore

// Chapter 5: run it with: go run run.go
package main

import (
	"fmt"

	loops "labbox/lab/05-loops"
)

func main() {
	fmt.Println(loops.SumTo(5), loops.SumTo(100), loops.SumTo(0))
	fmt.Println(loops.CountVowels("Hello World"), loops.CountVowels("rhythm"))
}
