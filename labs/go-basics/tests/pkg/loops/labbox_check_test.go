package loops

import (
	"encoding/json"
	"fmt"
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

func TestLabboxCheckSumTo(t *testing.T) {
	defer guard("sum_to")
	for _, c := range [][2]int{{5, 15}, {1, 1}, {0, 0}, {-3, 0}, {100, 5050}} {
		if got := SumTo(c[0]); got != c[1] {
			report("sum_to", false, fmt.Sprintf("SumTo(%d) returned %d", c[0], got), c[1], got)
			return
		}
	}
	report("sum_to", true, "Correct, and a loop that never runs leaves 0, so negative n is handled for free.", nil, nil)
}

func TestLabboxCheckCountVowels(t *testing.T) {
	defer guard("count_vowels")
	cases := map[string]int{"Hello World": 3, "AEIOU": 5, "rhythm": 0, "": 0, "Go is fun": 3, "naive jose": 5}
	for in, want := range cases {
		if got := CountVowels(in); got != want {
			report("count_vowels", false, fmt.Sprintf("CountVowels(%q) returned %d", in, got), want, got)
			return
		}
	}
	report("count_vowels", true, "Nice: range over a string gives runes, and one switch case lists all five vowels.", nil, nil)
}
