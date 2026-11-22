//go:build ignore

// Chapter 8: tidy an address typed in a hurry.
package main

import (
	"fmt"
	"strings"
)

func main() {
	typed := "   12 mg ROAD,  pune  "
	fmt.Printf("[%s]\n", typed)
	fmt.Printf("[%s]\n", strings.TrimSpace(typed))
	fmt.Println(strings.Fields(typed), len(strings.Fields(typed)))
	fmt.Println(strings.ToUpper("pune"), strings.Contains(typed, "ROAD"), strings.Split("a,b,,c", ","))
}
