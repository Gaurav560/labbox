//go:build ignore

// Chapter 5: Go has one loop, and it does every job.
package main

import "fmt"

func main() {
	weights := []int{4, 12, 7}
	total := 0
	for i := 0; i < len(weights); i++ {
		total += weights[i]
		fmt.Printf("stop %d: %d kg so far\n", i+1, total)
	}

	for i, w := range weights {
		fmt.Println(i, w)
	}

	fuel := 10
	for fuel > 0 {
		fuel -= 4
	}
	fmt.Println("fuel left:", fuel)
}
