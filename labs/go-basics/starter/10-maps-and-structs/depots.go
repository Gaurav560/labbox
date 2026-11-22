//go:build ignore

// Chapter 10: a map of depots, and a parcel as a struct.
package main

import "fmt"

type Parcel struct {
	ID     string
	Weight int
	City   string
}

func main() {
	p := Parcel{ID: "P-101", Weight: 4, City: "Pune"}
	fmt.Println(p)
	fmt.Printf("%+v\n", p)
	p.Weight = 5
	fmt.Println(p.Weight)

	waiting := map[string]int{"Pune": 3, "Delhi": 7}
	waiting["Pune"]++
	fmt.Println(waiting["Pune"], waiting["Goa"])
	n, ok := waiting["Goa"]
	fmt.Println(n, ok)
	fmt.Println(len(waiting))
}
