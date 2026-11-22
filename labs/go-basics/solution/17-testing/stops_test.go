// Chapter 17: tests for NextStop. Run them with: go test
package eta

import "testing"

func TestNextStopMovesOn(t *testing.T) {
	if got := NextStop(0, 3); got != 1 {
		t.Errorf("NextStop(0, 3) = %d, want 1", got)
	}
}

func TestNextStopWrapsToTheDepot(t *testing.T) {
	if got := NextStop(2, 3); got != 0 {
		t.Errorf("NextStop(2, 3) = %d, want 0: after the last stop, back to the depot", got)
	}
}
