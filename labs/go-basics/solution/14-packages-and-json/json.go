//go:build ignore

// Chapter 14: a parcel becomes JSON, and JSON becomes a parcel again.
package main

import (
	"encoding/json"
	"fmt"
)

type Parcel struct {
	ID      string `json:"id"`
	Weight  int    `json:"weight_kg"`
	City    string `json:"city,omitempty"`
	secret  string
	Fragile bool
}

func main() {
	p := Parcel{ID: "P-101", Weight: 4, secret: "only Go sees me", Fragile: true}
	data, err := json.Marshal(p)
	fmt.Println(string(data), err)

	var back Parcel
	err = json.Unmarshal([]byte(`{"id":"P-202","weight_kg":9,"city":"Goa","colour":"red"}`), &back)
	fmt.Printf("%+v %v\n", back, err)

	err = json.Unmarshal([]byte(`{"id": 42}`), &back)
	fmt.Println(err)
}
