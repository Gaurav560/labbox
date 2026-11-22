//go:build ignore

// Chapter 2: one function, two answers.
package main

import "fmt"

func minutesAndSeconds(total int) (int, int) {
	return total / 60, total % 60
}

func describe(name string, seconds int) string {
	m, s := minutesAndSeconds(seconds)
	return fmt.Sprintf("%s: %d min %d s", name, m, s)
}

func main() {
	fmt.Println(minutesAndSeconds(245))
	fmt.Println(describe("Pune to Mumbai", 9015))
	m, _ := minutesAndSeconds(130)
	fmt.Println(m)
}
