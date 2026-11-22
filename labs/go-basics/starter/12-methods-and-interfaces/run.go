//go:build ignore

// Chapter 12: run it with: go run run.go
package main

import (
	"fmt"

	shapes "labbox/lab/12-methods-and-interfaces"
)

func main() {
	fmt.Println(shapes.Rect{W: 3, H: 4}.Area(), shapes.Circle{R: 2}.Area())
	fmt.Println(shapes.TotalArea([]shapes.Shape{shapes.Rect{W: 3, H: 4}, shapes.Circle{R: 1}}))
}
