//go:build ignore

// Chapter 4: the price to ship a parcel, decided step by step.
package main

import "fmt"

func shipping(kg int) int {
	if kg <= 0 {
		return -1
	} else if kg <= 2 {
		return 60
	} else if kg <= 10 {
		return 120
	}
	return 250
}

func zone(city string) string {
	switch city {
	case "Pune", "Mumbai":
		return "west"
	case "Delhi":
		return "north"
	default:
		return "elsewhere"
	}
}

func main() {
	fmt.Println(shipping(1), shipping(2), shipping(3), shipping(30), shipping(0))
	fmt.Println(zone("Mumbai"), zone("Delhi"), zone("Goa"))
}
