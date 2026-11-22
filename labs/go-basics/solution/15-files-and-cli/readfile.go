//go:build ignore

// Chapter 15: read a whole file, line by line.
package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	f, err := os.Open("expenses.csv")
	if err != nil {
		fmt.Println("could not open:", err)
		return
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	n := 0
	for scanner.Scan() {
		n++
		if n <= 3 {
			fmt.Println(n, scanner.Text())
		}
	}
	fmt.Println(n, "lines")

	_, err = os.Open("nope.csv")
	fmt.Println(err)
}
