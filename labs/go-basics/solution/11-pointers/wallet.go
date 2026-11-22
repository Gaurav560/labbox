// Chapter 11: pointers. Run it with: go run run.go
package wallet

// Wallet holds a balance in rupees.
type Wallet struct {
	Balance int
}

// Deposit adds amount to the wallet.
func (w *Wallet) Deposit(amount int) {
	w.Balance += amount
}

// Swap exchanges the values a and b point to.
func Swap(a, b *int) {
	*a, *b = *b, *a
}
