// Chapter 3: making decisions.
package decisions

// Grade turns marks into "A", "B", "C" or "F", or "Invalid" outside 0 to 100.
func Grade(marks int) string {
	switch {
	case marks < 0 || marks > 100:
		return "Invalid"
	case marks >= 80:
		return "A"
	case marks >= 60:
		return "B"
	case marks >= 40:
		return "C"
	default:
		return "F"
	}
}

// IsLeapYear: divisible by 4, except by 100, except by 400.
func IsLeapYear(year int) bool {
	return year%4 == 0 && (year%100 != 0 || year%400 == 0)
}
