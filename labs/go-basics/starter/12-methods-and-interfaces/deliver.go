//go:build ignore

// Chapter 12: a bike and a van both deliver; one loop handles both.
package main

import "fmt"

type Deliverer interface {
	MinutesFor(km int) int
}

type Bike struct{}
type Van struct{ Stops int }

func (Bike) MinutesFor(km int) int  { return km * 4 }
func (v Van) MinutesFor(km int) int { return km*2 + v.Stops*5 }

func main() {
	fleet := []Deliverer{Bike{}, Van{Stops: 3}}
	for _, d := range fleet {
		fmt.Printf("%T: %d minutes for 10 km\n", d, d.MinutesFor(10))
	}
}
