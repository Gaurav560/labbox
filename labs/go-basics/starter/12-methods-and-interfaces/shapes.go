// Chapter 12: methods and interfaces. Run it with: go run run.go
package shapes

// Shape is anything with an area.
type Shape interface {
	Area() float64
}

// Rect is a rectangle W wide and H high.
type Rect struct{ W, H float64 }

// Circle is a circle with radius R.
type Circle struct{ R float64 }

// TODO (task areas): width times height.
func (r Rect) Area() float64 { return 0 }

// TODO (task areas): pi times the radius squared (math.Pi).
func (c Circle) Area() float64 { return 0 }

// TODO (task total_area): the sum of all the areas, rounded to 2 decimals.
func TotalArea(shapes []Shape) float64 {
	return 0
}
