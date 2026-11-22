// Chapter 2: functions. Run it with: go run run.go
package hello

// Greeting returns "Hello, <name>!".
func Greeting(name string) string {
	return "Hello, " + name + "!"
}

// TotalMinutes turns hours and minutes into minutes.
func TotalMinutes(hours, minutes int) int {
	return hours*60 + minutes
}
