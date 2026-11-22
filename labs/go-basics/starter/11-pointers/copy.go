//go:build ignore

// Chapter 11: why does the parcel not get heavier?
package main

import "fmt"

type Parcel struct {
	Weight int
}

func addBox(p Parcel) {
	p.Weight += 2
	fmt.Println("inside addBox:", p.Weight)
}

func addBoxReally(p *Parcel) {
	p.Weight += 2
}

func main() {
	parcel := Parcel{Weight: 4}
	addBox(parcel)
	fmt.Println("after addBox:", parcel.Weight)

	addBoxReally(&parcel)
	fmt.Println("after addBoxReally:", parcel.Weight)

	ptr := &parcel
	fmt.Println(ptr.Weight, *ptr, ptr == &parcel)
}
