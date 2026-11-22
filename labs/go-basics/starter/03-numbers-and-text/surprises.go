//go:build ignore

// Chapter 3: does Go get 0.1 + 0.2 right?
package main

import "fmt"

func main() {
	fmt.Println(0.1 + 0.2)
	a, b := 0.1, 0.2
	fmt.Println(a + b)
	fmt.Println(7/2, 7.0/2, float64(7)/2)
	var small int8 = 127
	small++
	fmt.Println(small)
	fmt.Printf("%.2f %5d| %q %T\n", 3.14159, 42, "box", 42)
}
