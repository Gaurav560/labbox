package till

import (
	"encoding/json"
	"fmt"
	"testing"
)

// Hidden checks for go-basics. Each test reports with @@RESULT and never fails, so every task reports.
func report(task string, passed bool, message string, expected, actual any) {
	if !passed && message != "" {
		message = "Not yet: " + message // Content standard: calm, never blaming
	}
	r := map[string]any{"task": task, "passed": passed, "message": message}
	if expected != nil {
		r["expected"], r["actual"] = fmt.Sprint(expected), fmt.Sprint(actual)
	}
	b, _ := json.Marshal(r)
	fmt.Println("@@RESULT " + string(b))
}

func guard(task string) {
	if p := recover(); p != nil {
		report(task, false, fmt.Sprintf("your code panicked: %v", p), nil, nil)
	}
}

func TestLabboxCheckTotal(t *testing.T) {
	defer guard("total")
	for _, c := range []struct {
		in   []int
		want int
	}{{[]int{1500, 2000}, 3500}, {nil, 0}, {[]int{1}, 1}} {
		if got := Total(c.in); got != c.want {
			report("total", false, fmt.Sprintf("Total(%v) returned %d", c.in, got), c.want, got)
			return
		}
	}
	report("total", true, "Correct: range over a slice, a running total, and nil works like an empty slice.", nil, nil)
}

func TestLabboxCheckParseAmount(t *testing.T) {
	defer guard("parse_amount")
	good := map[string]int{"12.50": 1250, "7": 700, "0.05": 5, "120.00": 12000}
	for in, want := range good {
		got, err := ParseAmount(in)
		if err != nil || got != want {
			report("parse_amount", false, fmt.Sprintf("ParseAmount(%q) returned %d, %v", in, got, err), want, got)
			return
		}
	}
	for _, in := range []string{"", "abc", "1.5", "-3", "12.505", "1.ab"} {
		if _, err := ParseAmount(in); err == nil {
			report("parse_amount", false, fmt.Sprintf("ParseAmount(%q) should return an error", in), "an error", "nil")
			return
		}
	}
	report("parse_amount", true, "Robust: every bad input comes back as an error, never a panic. That is idiomatic Go.", nil, nil)
}
