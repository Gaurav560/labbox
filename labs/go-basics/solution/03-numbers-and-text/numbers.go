// Chapter 3: numbers and text. Run it with: go run run.go
package numbers

import (
	"fmt"
	"math"
)

// Percent returns scored out of total as a percentage, rounded to one decimal; 0 when total is 0.
func Percent(scored, total int) float64 {
	if total == 0 {
		return 0
	}
	return math.Round(float64(scored)/float64(total)*1000) / 10
}

// FormatRupees shows an amount in paise as rupees, like "₹12.50".
func FormatRupees(paise int) string {
	return fmt.Sprintf("₹%d.%02d", paise/100, paise%100)
}
