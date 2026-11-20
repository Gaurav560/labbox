// Chapter 10: errors in depth.
package bank

import "errors"

// ErrInsufficientFunds is returned (wrapped) when a withdrawal is bigger than the balance.
var ErrInsufficientFunds = errors.New("insufficient funds")

// TODO (task withdraw): the new balance; an error for amount <= 0; a wrapped ErrInsufficientFunds when
// amount > balance (callers check it with errors.Is). On an error, return the balance unchanged.
func Withdraw(balance, amount int) (int, error) {
	return balance, nil
}

// TODO (task parse_age): a whole number from 0 to 150; wrap strconv's error with %w; an error out of range.
func ParseAge(text string) (int, error) {
	return 0, nil
}
