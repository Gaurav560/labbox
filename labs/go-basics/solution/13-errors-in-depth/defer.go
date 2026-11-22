//go:build ignore

// Chapter 13: defer runs on the way out, last in, first out.
package main

import "fmt"

func deliver(stop string) {
	fmt.Println("open the van doors")
	defer fmt.Println("close the van doors")
	defer fmt.Println("lock the van")
	fmt.Println("hand over the parcel at", stop)
}

func main() {
	deliver("MG Road")
}
