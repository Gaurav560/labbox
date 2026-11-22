//go:build ignore

// Chapter 16: many goroutines write one map at the same time.
package main

import (
	"fmt"
	"sync"
)

func main() {
	counts := map[string]int{}
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				counts["parcels"]++
			}
		}()
	}
	wg.Wait()
	fmt.Println(counts["parcels"])
}
