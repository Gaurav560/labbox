// Chapter 7: more slices.
package slicetools

import "slices"

// TopN returns the n biggest numbers, biggest first, without changing the slice it was given.
func TopN(numbers []int, n int) []int {
	sorted := slices.Clone(numbers)
	slices.Sort(sorted)
	slices.Reverse(sorted)
	return sorted[:max(0, min(n, len(sorted)))]
}

// Unique returns each item once, in the order it first appeared.
func Unique(items []string) []string {
	seen := map[string]bool{}
	result := []string{}
	for _, it := range items {
		if !seen[it] {
			seen[it] = true
			result = append(result, it)
		}
	}
	return result
}
