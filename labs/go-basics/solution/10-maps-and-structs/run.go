//go:build ignore

// Chapter 10: run it with: go run run.go
package main

import (
	"fmt"

	orders "labbox/lab/10-maps-and-structs"
)

func main() {
	sales := []orders.Order{{Item: "box", Qty: 2}, {Item: "tape", Qty: 1}, {Item: "box", Qty: 1}}
	fmt.Println(orders.CountByItem(sales), orders.Busiest(sales))
}
