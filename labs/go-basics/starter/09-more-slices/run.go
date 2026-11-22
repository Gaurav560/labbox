//go:build ignore

// Chapter 9: run it with: go run run.go
package main

import (
	"fmt"

	slicetools "labbox/lab/09-more-slices"
)

func main() {
	marks := []int{72, 45, 90, 66}
	fmt.Println(slicetools.TopN(marks, 2), marks)
	fmt.Println(slicetools.Unique([]string{"Pune", "Goa", "Pune"}))
}
