//go:build ignore

// Chapter 6: ask the van functions small questions. Run it with: go run ask.go
package main

import (
	"fmt"

	van "labbox/lab/06-finding-bugs"
)

func main() {
	fmt.Println(van.TotalWeight([]int{4, 12, 7}))
	fmt.Println(van.TotalWeight([]int{4}))
	fmt.Println(van.CanLoad(10, 10))
}
