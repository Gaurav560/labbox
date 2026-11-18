package lab

import (
	"encoding/json"
	"fmt"
	"testing"
)

// report prints one @@RESULT line; a test never fails on purpose, so every task always reports.
func report(task string, passed bool, message string, expected, actual any) {
	r := map[string]any{"task": task, "passed": passed, "message": message}
	if expected != nil {
		r["expected"], r["actual"] = fmt.Sprint(expected), fmt.Sprint(actual)
	}
	b, _ := json.Marshal(r)
	fmt.Println("@@RESULT " + string(b))
}

func TestLabboxCheckDouble(t *testing.T) {
	defer func() {
		if p := recover(); p != nil {
			report("double", false, fmt.Sprintf("Double panicked: %v", p), nil, nil)
		}
	}()
	for _, c := range [][2]int{{21, 42}, {0, 0}, {-3, -6}} {
		if got := Double(c[0]); got != c[1] {
			report("double", false, fmt.Sprintf("Double(%d) returned %d", c[0], got), c[1], got)
			return
		}
	}
	report("double", true, "ok", nil, nil)
}
