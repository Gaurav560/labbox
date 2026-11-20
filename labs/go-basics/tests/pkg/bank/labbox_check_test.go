package bank

import (
	"encoding/json"
	"fmt"
	"errors"
	"strconv"
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

func TestLabboxCheckWithdraw(t *testing.T) {
	defer guard("withdraw")
	if got, err := Withdraw(500, 200); err != nil || got != 300 {
		report("withdraw", false, fmt.Sprintf("Withdraw(500, 200) returned %d, %v", got, err), "300 <nil>", fmt.Sprint(got, " ", err))
		return
	}
	if got, err := Withdraw(500, 500); err != nil || got != 0 {
		report("withdraw", false, fmt.Sprintf("Withdraw(500, 500) returned %d, %v: taking everything is allowed", got, err), "0 <nil>", fmt.Sprint(got, " ", err))
		return
	}
	got, err := Withdraw(100, 250)
	if err == nil {
		report("withdraw", false, "Withdraw(100, 250) should return an error", "an error", "nil")
		return
	}
	if !errors.Is(err, ErrInsufficientFunds) {
		report("withdraw", false, fmt.Sprintf("Withdraw(100, 250) returned %q, but errors.Is(err, ErrInsufficientFunds) is false: wrap it with %%w", err), "true", "false")
		return
	}
	if got != 100 {
		report("withdraw", false, fmt.Sprintf("On an error the balance should stay 100; Withdraw returned %d", got), 100, got)
		return
	}
	for _, amount := range []int{0, -50} {
		if _, err := Withdraw(100, amount); err == nil || errors.Is(err, ErrInsufficientFunds) {
			report("withdraw", false, fmt.Sprintf("Withdraw(100, %d) should return an invalid amount error (not insufficient funds); got %v", amount, err), "an error", err)
			return
		}
	}
	report("withdraw", true, "Wrapped with %w: callers can check errors.Is(err, ErrInsufficientFunds), and the message still says how much.", nil, nil)
}

func TestLabboxCheckParseAge(t *testing.T) {
	defer guard("parse_age")
	for in, want := range map[string]int{"17": 17, "0": 0, "150": 150} {
		if got, err := ParseAge(in); err != nil || got != want {
			report("parse_age", false, fmt.Sprintf("ParseAge(%q) returned %d, %v", in, got, err), want, got)
			return
		}
	}
	_, err := ParseAge("abc")
	if err == nil || !errors.Is(err, strconv.ErrSyntax) {
		report("parse_age", false, fmt.Sprintf("ParseAge(\"abc\") returned %v: wrap strconv's error with %%w so errors.Is(err, strconv.ErrSyntax) works", err), "a wrapped strconv error", err)
		return
	}
	var numErr *strconv.NumError
	if !errors.As(err, &numErr) {
		report("parse_age", false, "errors.As should find the *strconv.NumError inside your error", "a wrapped *strconv.NumError", err)
		return
	}
	for _, in := range []string{"-1", "151", "", "12.5"} {
		if _, err := ParseAge(in); err == nil {
			report("parse_age", false, fmt.Sprintf("ParseAge(%q) should return an error", in), "an error", "nil")
			return
		}
	}
	report("parse_age", true, "Your error keeps strconv's error inside, so errors.Is and errors.As both work for the caller.", nil, nil)
}
