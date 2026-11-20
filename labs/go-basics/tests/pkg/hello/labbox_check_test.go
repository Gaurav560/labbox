package hello

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

func TestLabboxCheckGreeting(t *testing.T) {
	defer guard("greeting")
	for in, want := range map[string]string{"Asha": "Hello, Asha!", "World": "Hello, World!", "": "Hello, !"} {
		if got := Greeting(in); got != want {
			report("greeting", false, fmt.Sprintf("Greeting(%q) returned %q", in, got), want, got)
			return
		}
	}
	report("greeting", true, "Your first Go function works: typed input, typed output, joined text. Every Go program is built from pieces like this.", nil, nil)
}

func TestLabboxCheckTotalMinutes(t *testing.T) {
	defer guard("total_minutes")
	for _, c := range [][3]int{{2, 15, 135}, {0, 45, 45}, {1, 0, 60}, {0, 0, 0}, {10, 59, 659}} {
		if got := TotalMinutes(c[0], c[1]); got != c[2] {
			report("total_minutes", false, fmt.Sprintf("TotalMinutes(%d, %d) returned %d", c[0], c[1], got), c[2], got)
			return
		}
	}
	report("total_minutes", true, "Correct. Several parameters of one type can share it: (hours, minutes int).", nil, nil)
}
