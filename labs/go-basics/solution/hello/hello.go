// Chapter 1: your first Go program.
package hello

// Greeting returns "Hello, <name>!".
func Greeting(name string) string {
	return "Hello, " + name + "!"
}

// TotalMinutes turns hours and minutes into minutes.
func TotalMinutes(hours, minutes int) int {
	return hours*60 + minutes
}
