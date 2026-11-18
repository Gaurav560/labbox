package lab

// Order is one line on a till receipt.
type Order struct {
	Item string
	Qty  int
}

// TODO (task total): the sum of all prices (in paise).
func Total(prices []int) int {
	return 0
}

// TODO (task parse_amount): "12.50" -> 1250 paise, "7" -> 700.
// Anything else ("", "abc", "1.5", "-3") returns 0 and an error.
func ParseAmount(text string) (int, error) {
	return 0, nil
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
