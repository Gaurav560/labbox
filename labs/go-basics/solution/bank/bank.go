// Chapter 10: errors in depth.
package bank

import (
	"errors"
	"fmt"
	"strconv"
)

// ErrInsufficientFunds is returned (wrapped) when a withdrawal is bigger than the balance.
var ErrInsufficientFunds = errors.New("insufficient funds")

// Withdraw takes amount out of balance and returns the new balance.
func Withdraw(balance, amount int) (int, error) {
	if amount <= 0 {
		return balance, fmt.Errorf("invalid amount %d", amount)
	}
	if amount > balance {
		return balance, fmt.Errorf("withdraw %d from %d: %w", amount, balance, ErrInsufficientFunds)
	}
	return balance - amount, nil
}

// ParseAge reads an age from text: a whole number from 0 to 150.
func ParseAge(text string) (int, error) {
	age, err := strconv.Atoi(text)
	if err != nil {
		return 0, fmt.Errorf("age %q: %w", text, err)
	}
	if age < 0 || age > 150 {
		return 0, fmt.Errorf("age %d is out of range", age)
	}
	return age, nil
}
