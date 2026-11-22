//go:build ignore

// Chapter 12: teach fmt how to print your type.
package main

import "fmt"

type Parcel struct {
	ID     string
	Weight int
}

func (p Parcel) String() string {
	return fmt.Sprintf("parcel %s (%d kg)", p.ID, p.Weight)
}

func main() {
	p := Parcel{ID: "P-101", Weight: 4}
	fmt.Println(p)
	fmt.Println([]Parcel{p, {ID: "P-102", Weight: 9}})
}
