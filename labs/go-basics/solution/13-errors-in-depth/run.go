//go:build ignore

// Chapter 13: run it with: go run run.go
package main

import (
	"errors"
	"fmt"

	bank "labbox/lab/13-errors-in-depth"
)

func main() {
	fmt.Println(bank.Withdraw(500, 200))
	_, err := bank.Withdraw(100, 500)
	fmt.Println(err, errors.Is(err, bank.ErrInsufficientFunds))
	fmt.Println(bank.ParseAge("42"))
	fmt.Println(bank.ParseAge("forty"))
}
