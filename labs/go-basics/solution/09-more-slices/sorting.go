//go:build ignore

// Chapter 9: sort a copy, not the original.
package main

import (
	"fmt"
	"slices"
)

func main() {
	weights := []int{12, 4, 9}
	sorted := slices.Clone(weights)
	slices.Sort(sorted)
	fmt.Println(weights, sorted)
	slices.Reverse(sorted)
	fmt.Println(sorted, slices.Contains(weights, 9), slices.Index(weights, 9))
}
