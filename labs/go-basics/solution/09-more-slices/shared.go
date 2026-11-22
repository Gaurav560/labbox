//go:build ignore

// Chapter 9: two slices, one secret.
package main

import "fmt"

func main() {
	van := []int{4, 12, 7, 9}
	front := van[:2]
	front[0] = 99
	fmt.Println(van, front)

	front = append(front, 50)
	fmt.Println(van, front)

	safe := make([]int, len(van))
	copy(safe, van)
	safe[0] = 1
	fmt.Println(van[0], safe[0], len(front), cap(front))
}
