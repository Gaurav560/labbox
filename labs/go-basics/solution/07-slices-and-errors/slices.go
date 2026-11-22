//go:build ignore

// Chapter 7: a slice that grows.
package main

import "fmt"

func main() {
	var weights []int
	fmt.Println(weights, len(weights), weights == nil)
	weights = append(weights, 4)
	weights = append(weights, 12, 7)
	fmt.Println(weights, len(weights), weights[0], weights[len(weights)-1])
	fmt.Println(weights[1:3])
}
