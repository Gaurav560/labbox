//go:build ignore

// Chapter 16: three deliveries at once. Or are they?
package main

import (
	"fmt"
	"time"
)

func deliver(stop string) {
	time.Sleep(100 * time.Millisecond)
	fmt.Println("delivered to", stop)
}

func main() {
	for _, stop := range []string{"MG Road", "FC Road", "JM Road"} {
		go deliver(stop)
	}
	fmt.Println("all sent!")
}
