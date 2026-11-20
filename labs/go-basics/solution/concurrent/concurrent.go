// Chapter 13: goroutines and channels.
package concurrent

import (
	"strings"
	"sync"
)

// FetchAll calls fetch for every item at the same time and returns the results in the items' order.
func FetchAll(items []string, fetch func(string) string) []string {
	results := make([]string, len(items))
	var wg sync.WaitGroup
	for i, it := range items {
		wg.Add(1)
		go func() {
			defer wg.Done()
			results[i] = fetch(it)
		}()
	}
	wg.Wait()
	return results
}

// CountWords counts every word (lower case) across all texts, one goroutine per text.
func CountWords(texts []string) map[string]int {
	counts := map[string]int{}
	var mu sync.Mutex
	var wg sync.WaitGroup
	for _, t := range texts {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for _, w := range strings.Fields(strings.ToLower(t)) {
				mu.Lock()
				counts[w]++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()
	return counts
}
