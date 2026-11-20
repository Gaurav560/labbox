package decisions

import (
	"encoding/json"
	"fmt"
	"testing"
)

// Hidden checks (LabBox). Each test reports with @@RESULT and never fails, so every task reports.
func report(task string, passed bool, message string, expected, actual any) {
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

func TestLabboxCheckGrade(t *testing.T) {
	defer guard("grade")
	cases := []struct {
		in   int
		want string
	}{{95, "A"}, {80, "A"}, {79, "B"}, {60, "B"}, {59, "C"}, {40, "C"}, {39, "F"}, {100, "A"}, {0, "F"}, {101, "Invalid"}, {-1, "Invalid"}}
	for _, c := range cases {
		if got := Grade(c.in); got != c.want {
			report("grade", false, fmt.Sprintf("Grade(%d) returned %q", c.in, got), c.want, got)
			return
		}
	}
	report("grade", true, "ok", nil, nil)
}

func TestLabboxCheckLeapYear(t *testing.T) {
	defer guard("leap_year")
	cases := map[int]bool{2024: true, 2023: false, 1900: false, 2000: true, 2100: false, 1600: true, 2019: false}
	for in, want := range cases {
		if got := IsLeapYear(in); got != want {
			report("leap_year", false, fmt.Sprintf("IsLeapYear(%d) returned %v", in, got), want, got)
			return
		}
	}
	report("leap_year", true, "ok", nil, nil)
}
