//go:build ignore

// Chapter 8: run it with: go run run.go
package main

import (
	"fmt"

	words "labbox/lab/08-strings"
)

func main() {
	fmt.Println(words.CountWords("Go is fun"), words.CountWords("  lots   of   spaces  "))
	fmt.Printf("[%s]\n", words.CleanName("  riya   SHARMA "))
}
