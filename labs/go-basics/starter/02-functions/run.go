//go:build ignore

// Chapter 2: run it with: go run run.go
package main

import (
	"fmt"

	hello "labbox/lab/02-functions"
)

func main() {
	fmt.Println(hello.Greeting("Asha"))
	fmt.Println(hello.TotalMinutes(2, 15))
}
