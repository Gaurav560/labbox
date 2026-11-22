//go:build ignore

// Chapter 6: a crash two functions deep.
package main

import "fmt"

func heaviest(weights []int) int {
	best := weights[0]
	for _, w := range weights {
		if w > best {
			best = w
		}
	}
	return best
}

func summary(van string, weights []int) string {
	return fmt.Sprintf("%s: heaviest parcel %d kg", van, heaviest(weights))
}

func main() {
	fmt.Println(summary("Morning van", []int{4, 12, 7}))
	fmt.Println(summary("Evening van", []int{}))
}
