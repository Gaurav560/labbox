//go:build ignore

// Chapter 8: how long is the name José?
package main

import (
	"fmt"
	"unicode/utf8"
)

func main() {
	word := "José"
	fmt.Println(len(word), utf8.RuneCountInString(word))
	fmt.Println(word[3], string(word[3]))
	for i, r := range word {
		fmt.Println(i, string(r))
	}
}
