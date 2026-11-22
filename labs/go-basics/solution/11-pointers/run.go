//go:build ignore

// Chapter 11: run it with: go run run.go
package main

import (
	"fmt"

	wallet "labbox/lab/11-pointers"
)

func main() {
	w := wallet.Wallet{Balance: 100}
	w.Deposit(50)
	w.Deposit(25)
	fmt.Println(w.Balance)
	x, y := 1, 2
	wallet.Swap(&x, &y)
	fmt.Println(x, y)
}
