//go:build ignore

// Chapter 4: is 0 false in Go?
package main

import "fmt"

func main() {
	parcels := 0
	if parcels {
		fmt.Println("the van has parcels")
	}
}
