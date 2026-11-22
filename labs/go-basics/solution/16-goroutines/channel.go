//go:build ignore

// Chapter 16: goroutines report back through a channel.
package main

import "fmt"

func weigh(parcel string, kg int, results chan<- string) {
	results <- fmt.Sprintf("%s weighs %d kg", parcel, kg)
}

func main() {
	results := make(chan string)
	go weigh("P-1", 4, results)
	go weigh("P-2", 12, results)
	go weigh("P-3", 7, results)
	for i := 0; i < 3; i++ {
		fmt.Println(<-results)
	}
}
