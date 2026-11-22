//go:build ignore

// Chapter 1: no typo in this file, yet it stops halfway.
package main

import "fmt"

func main() {
	parcels := []string{"Books", "Lamp"}
	fmt.Println("Parcels:", len(parcels))
	next := 5
	fmt.Println("Next up:", parcels[next])
	fmt.Println("This line never runs.")
}
