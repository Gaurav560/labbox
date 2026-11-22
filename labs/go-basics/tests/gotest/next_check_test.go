package eta

import "testing"

func TestHiddenNextStop(t *testing.T) {
	for _, c := range []struct{ index, count, want int }{{0, 3, 1}, {1, 3, 2}, {2, 3, 0}, {4, 5, 0}, {0, 1, 0}} {
		if got := NextStop(c.index, c.count); got != c.want {
			t.Errorf("NextStop(%d, %d) = %d, want %d", c.index, c.count, got, c.want)
		}
	}
}
