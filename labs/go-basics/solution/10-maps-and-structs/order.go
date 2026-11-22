//go:build ignore

// Chapter 10: in what order does a map hand you its keys?
package main

import "fmt"

func main() {
	waiting := map[string]int{"Pune": 3, "Delhi": 7, "Goa": 1, "Kochi": 2, "Agra": 5}
	for round := 1; round <= 3; round++ {
		fmt.Print("round ", round, ":")
		for city := range waiting {
			fmt.Print(" ", city)
		}
		fmt.Println()
	}
}
