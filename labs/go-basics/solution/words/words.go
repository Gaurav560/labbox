// Chapter 6: strings.
package words

import "strings"

// CleanName trims a name, keeps one space between words, and capitalises each word.
func CleanName(raw string) string {
	parts := strings.Fields(raw)
	for i, w := range parts {
		parts[i] = strings.ToUpper(w[:1]) + strings.ToLower(w[1:])
	}
	return strings.Join(parts, " ")
}

// CountWords counts the words separated by spaces, tabs or new lines.
func CountWords(text string) int {
	return len(strings.Fields(text))
}
