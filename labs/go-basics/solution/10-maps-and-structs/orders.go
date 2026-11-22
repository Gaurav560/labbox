// Chapter 10: the depot counter's sales. Run it with: go run run.go
package orders

// Order is one line on a till receipt.
type Order struct {
	Item string
	Qty  int
}

func CountByItem(orders []Order) map[string]int {
	counts := make(map[string]int)
	for _, o := range orders {
		counts[o.Item] += o.Qty
	}
	return counts
}

func Busiest(orders []Order) string {
	best, bestCount := "", 0
	for item, n := range CountByItem(orders) {
		if n > bestCount || (n == bestCount && item < best) {
			best, bestCount = item, n
		}
	}
	return best
}
