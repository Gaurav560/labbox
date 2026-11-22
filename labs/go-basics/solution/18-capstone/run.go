//go:build ignore

// Chapter 18: run it with: go run run.go
package main

import (
	"fmt"

	report "labbox/lab/18-capstone"
)

func main() {
	r, err := report.DepotReport("deliveries.csv")
	fmt.Printf("%d delivered, %d kg, %.1f min on average %v\n", r.Delivered, r.TotalKg, r.AvgMins, err)
	fmt.Println(r.PerDepot, "busiest:", report.BusiestDepot(r))
	fmt.Println("bad lines:", r.BadLines)
}
