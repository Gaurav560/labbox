//go:build ignore

// Chapter 14: run it with: go run run.go
package main

import (
	"fmt"

	manifest "labbox/lab/14-packages-and-json"
)

func main() {
	data, err := manifest.SaveManifest("Van 7", []manifest.Parcel{{ID: "P-101", Weight: 4, City: "Pune"}})
	fmt.Println(string(data), err)
	parcels, err := manifest.LoadManifest([]byte(`{"van":"Van 9","parcels":[{"id":"P-202","weight_kg":9,"city":"Goa"}]}`))
	fmt.Println(parcels, err)
}
