//go:build ignore

// Chapter 11: a pointer to nothing.
package main

import "fmt"

type Parcel struct {
	Weight int
}

func main() {
	var p *Parcel
	fmt.Println(p == nil)
	fmt.Println(p.Weight)
}
