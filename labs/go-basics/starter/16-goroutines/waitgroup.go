//go:build ignore

// Chapter 16: wait for every goroutine, and time it.
package main

import (
	"fmt"
	"sync"
	"time"
)

func deliver(stop string) {
	time.Sleep(300 * time.Millisecond)
}

func main() {
	stops := []string{"MG Road", "FC Road", "JM Road"}

	start := time.Now()
	for _, stop := range stops {
		deliver(stop)
	}
	fmt.Println("one by one:", time.Since(start).Round(100*time.Millisecond))

	start = time.Now()
	var wg sync.WaitGroup
	for _, stop := range stops {
		wg.Add(1)
		go func() {
			defer wg.Done()
			deliver(stop)
		}()
	}
	wg.Wait()
	fmt.Println("all at once:", time.Since(start).Round(100*time.Millisecond))
}
