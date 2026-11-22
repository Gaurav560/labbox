// Chapter 10: the depot counter's sales. Run it with: go run run.go
package orders

// Order is one line on a till receipt.
type Order struct {
	Item string
	Qty  int
}

// TODO (task count_by_item): item -> total quantity ordered.
func CountByItem(orders []Order) map[string]int {
	return nil
}

// TODO (task busiest): the item with the biggest total quantity. Ties: the name that sorts first.
// No orders: "".
func Busiest(orders []Order) string {
	return ""
}
