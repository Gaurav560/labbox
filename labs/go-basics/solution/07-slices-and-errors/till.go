// Chapter 7: the depot counter's till. Run it with: go run run.go
package till

import (
	"errors"
	"strconv"
	"strings"
)

func Total(prices []int) int {
	total := 0
	for _, p := range prices {
		total += p
	}
	return total
}

var errAmount = errors.New("amount must look like 12 or 12.50")

func ParseAmount(text string) (int, error) {
	rupeesText, paiseText, hasDot := strings.Cut(strings.TrimSpace(text), ".")
	if hasDot && len(paiseText) != 2 {
		return 0, errAmount
	}
	rupees, err := strconv.Atoi(rupeesText)
	if err != nil || rupees < 0 || strings.HasPrefix(rupeesText, "+") {
		return 0, errAmount
	}
	paise := 0
	if hasDot {
		paise, err = strconv.Atoi(paiseText)
		if err != nil || paise < 0 || strings.HasPrefix(paiseText, "+") {
			return 0, errAmount
		}
	}
	return rupees*100 + paise, nil
}
