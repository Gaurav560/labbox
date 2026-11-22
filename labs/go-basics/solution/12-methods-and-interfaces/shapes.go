// Chapter 12: methods and interfaces. Run it with: go run run.go
package shapes

import "math"

// Shape is anything with an area.
type Shape interface {
	Area() float64
}

// Rect is a rectangle W wide and H high.
type Rect struct{ W, H float64 }

// Circle is a circle with radius R.
type Circle struct{ R float64 }

func (r Rect) Area() float64   { return r.W * r.H }
func (c Circle) Area() float64 { return math.Pi * c.R * c.R }

// TotalArea adds up the areas, rounded to 2 decimals.
func TotalArea(shapes []Shape) float64 {
	total := 0.0
	for _, s := range shapes {
		total += s.Area()
	}
	return math.Round(total*100) / 100
}
