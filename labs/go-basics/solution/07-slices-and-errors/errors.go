//go:build ignore

// Chapter 7: in Go, an error is just a value you are handed back.
package main

import (
	"fmt"
	"strconv"
)

func main() {
	for _, text := range []string{"42", "twelve", "7"} {
		n, err := strconv.Atoi(text)
		if err != nil {
			fmt.Println("problem:", err)
			continue
		}
		fmt.Println("parcel weighs", n, "kg")
	}
}
