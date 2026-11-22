//go:build ignore

// Chapter 16: run it with: go run run.go
package main

import (
	"fmt"

	concurrent "labbox/lab/16-goroutines"
)

func main() {
	shout := func(s string) string { return s + "!" }
	fmt.Println(concurrent.FetchAll([]string{"MG Road", "FC Road"}, shout))
	fmt.Println(concurrent.CountWords([]string{"go go", "Go fast"}))
}
