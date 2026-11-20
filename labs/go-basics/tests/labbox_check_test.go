package lab

import (
	"encoding/json"
	"fmt"
	"reflect"
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

func TestLabboxCheckCountByItem(t *testing.T) {
	defer guard("count_by_item")
	orders := []Order{{"coffee", 2}, {"vada pav", 1}, {"coffee", 1}, {"poha", 4}}
	want := map[string]int{"coffee": 3, "vada pav": 1, "poha": 4}
	if got := CountByItem(orders); !reflect.DeepEqual(got, want) {
		report("count_by_item", false, "CountByItem does not add up the quantities per item.", want, got)
		return
	}
	if got := CountByItem(nil); got == nil || len(got) != 0 {
		report("count_by_item", false, "CountByItem(nil) should return an empty map, not nil.", "map[]", got)
		return
	}
	report("count_by_item", true, "Correct counts, and an empty map (not nil) for no orders.", nil, nil)
}

func TestLabboxCheckBusiest(t *testing.T) {
	defer guard("busiest")
	cases := []struct {
		in   []Order
		want string
	}{
		{[]Order{{"coffee", 2}, {"vada pav", 1}, {"coffee", 1}}, "coffee"},
		{[]Order{{"poha", 3}, {"bun", 3}, {"coffee", 2}}, "bun"},
		{nil, ""},
	}
	for _, c := range cases {
		for i := 0; i < 20; i++ { // map order is random: try many times
			if got := Busiest(c.in); got != c.want {
				report("busiest", false, fmt.Sprintf("Busiest(%v) returned %q", c.in, got), c.want, got)
				return
			}
		}
	}
	report("busiest", true, "Fair every time, even though map order is random: your tie rule makes the answer stable.", nil, nil)
}
