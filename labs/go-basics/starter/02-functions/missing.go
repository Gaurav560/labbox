//go:build ignore

// Chapter 2: what if you forget an argument?
package main

import "fmt"

func describe(name string, seconds int) string {
	return fmt.Sprintf("%s: %d s", name, seconds)
}

func main() {
	fmt.Println(describe("Pune to Mumbai"))
}
