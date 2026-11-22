//go:build ignore

// Chapter 1: Go refuses to run this file. Fix it, and it prints three lines.
package main

import (
	"fmt"
)

func main() {
	count := 12
	fmt.Println("Parcel is starting...")
	fmt.Println("Ready to track your deliveries.")
	fmt.Println("Parcels on the van:", count)
}
