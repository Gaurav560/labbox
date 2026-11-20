// Chapter 4: loops.
package loops

import "unicode"

// SumTo adds up 1 + 2 + ... + n; 0 when n is 0 or negative.
func SumTo(n int) int {
	total := 0
	for i := 1; i <= n; i++ {
		total += i
	}
	return total
}

// CountVowels counts a, e, i, o and u, in either case.
func CountVowels(text string) int {
	count := 0
	for _, r := range text {
		switch unicode.ToLower(r) {
		case 'a', 'e', 'i', 'o', 'u':
			count++
		}
	}
	return count
}
