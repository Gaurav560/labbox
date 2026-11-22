// Chapter 11: pointers. Run it with: go run run.go
package wallet

// Wallet holds a balance in rupees.
type Wallet struct {
	Balance int
}

// TODO (task deposit): this does not work. Find out why the balance never changes, and fix it.
func (w Wallet) Deposit(amount int) {
	w.Balance += amount
}

// TODO (task swap): exchange the values a and b point to.
func Swap(a, b *int) {
}
