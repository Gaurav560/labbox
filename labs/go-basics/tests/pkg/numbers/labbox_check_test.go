package numbers

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

func TestLabboxCheckPercent(t *testing.T) {
	defer guard("percent")
	cases := []struct {
		s, t int
		want float64
	}{{45, 50, 90}, {1, 3, 33.3}, {2, 3, 66.7}, {0, 50, 0}, {7, 0, 0}, {50, 50, 100}}
	for _, c := range cases {
		if got := Percent(c.s, c.t); got != c.want {
			msg := fmt.Sprintf("Percent(%d, %d) returned %v", c.s, c.t, got)
			if got == 0 && c.want != 0 {
				msg += ": dividing two ints in Go throws the fraction away; convert to float64 first"
			}
			report("percent", false, msg, c.want, got)
			return
		}
	}
	report("percent", true, "Right, including 0 out of 0. Converting to float64 before dividing is the habit that avoids Go's integer division trap.", nil, nil)
}

func TestLabboxCheckFormatRupees(t *testing.T) {
	defer guard("format_rupees")
	cases := map[int]string{1250: "₹12.50", 5: "₹0.05", 0: "₹0.00", 120000: "₹1200.00", 99: "₹0.99", 100: "₹1.00"}
	for in, want := range cases {
		if got := FormatRupees(in); got != want {
			report("format_rupees", false, fmt.Sprintf("FormatRupees(%d) returned %q", in, got), want, got)
			return
		}
	}
	report("format_rupees", true, "Spot on: %02d keeps the paise at two digits, so 5 paise shows as 0.05.", nil, nil)
}
