// Chapter 16: goroutines and channels. Run it with: go run run.go
package concurrent

// TODO (task fetch_all): call fetch for every item at the same time; results in the items' order.
func FetchAll(items []string, fetch func(string) string) []string {
	results := make([]string, len(items))
	for i, it := range items {
		results[i] = fetch(it)
	}
	return results
}

// TODO (task word_counts): count every word (lower case) across all texts, one goroutine per text.
func CountWords(texts []string) map[string]int {
	return map[string]int{}
}
