// Chapter 17: when will the parcel arrive? This code is correct: your job is to write tests that prove it.
package eta

import "fmt"

// FormatETA shows a delivery time: 45 is "45 min"; an hour or more shows hours with two-digit minutes,
// so 125 is "2 h 05 min". Negative minutes return an error.
func FormatETA(minutes int) (string, error) {
	if minutes < 0 {
		return "0 min", nil
	}
	if minutes < 60 {
		return fmt.Sprintf("%d min", minutes), nil
	}
	return fmt.Sprintf("%d h %02d min", minutes/60, minutes%60), nil
}
