package shapes

import (
	"encoding/json"
	"fmt"
	"math"
	"testing"
)

// Hidden checks (LabBox). Each test reports with @@RESULT and never fails, so every task reports.
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

func TestLabboxCheckAreas(t *testing.T) {
	defer guard("areas")
	if got := (Rect{W: 3, H: 4}).Area(); got != 12 {
		report("areas", false, fmt.Sprintf("Rect{3, 4}.Area() returned %v", got), 12, got)
		return
	}
	if got := (Circle{R: 2}).Area(); math.Abs(got-4*math.Pi) > 1e-9 {
		report("areas", false, fmt.Sprintf("Circle{2}.Area() returned %v", got), 4*math.Pi, got)
		return
	}
	if got := (Rect{}).Area(); got != 0 {
		report("areas", false, fmt.Sprintf("Rect{}.Area() returned %v", got), 0, got)
		return
	}
	report("areas", true, "Both methods work: a method is just a function with a receiver.", nil, nil)
}

func TestLabboxCheckTotalArea(t *testing.T) {
	defer guard("total_area")
	cases := []struct {
		in   []Shape
		want float64
	}{{[]Shape{Rect{3, 4}, Circle{1}}, 15.14}, {[]Shape{Circle{2}, Circle{2}}, 25.13}, {nil, 0}, {[]Shape{Rect{2.5, 2}}, 5}}
	for _, c := range cases {
		if got := TotalArea(c.in); got != c.want {
			report("total_area", false, fmt.Sprintf("TotalArea(%v) returned %v", c.in, got), c.want, got)
			return
		}
	}
	report("total_area", true, "Any type with Area() is a Shape, so your function works for shapes nobody has written yet.", nil, nil)
}
