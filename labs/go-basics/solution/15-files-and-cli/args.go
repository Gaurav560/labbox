//go:build ignore

// Chapter 15: the words typed after the program's name, and flags.
package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	fmt.Println(len(os.Args), os.Args[1:])
	top := flag.Int("top", 3, "how many categories to show")
	flag.Parse()
	fmt.Println("top:", *top, "files:", flag.Args())
	if flag.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "usage: go run args.go [-top N] <file.csv>")
		os.Exit(2)
	}
}
