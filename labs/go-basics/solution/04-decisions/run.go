//go:build ignore

// Chapter 4: run it with: go run run.go
package main

import (
	"fmt"

	decisions "labbox/lab/04-decisions"
)

func main() {
	fmt.Println(decisions.Grade(80), decisions.Grade(79), decisions.Grade(39), decisions.Grade(101))
	fmt.Println(decisions.IsLeapYear(2024), decisions.IsLeapYear(1900), decisions.IsLeapYear(2000))
}
