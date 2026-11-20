package wallet

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

func TestLabboxCheckDeposit(t *testing.T) {
	defer guard("deposit")
	w := Wallet{Balance: 100}
	w.Deposit(50)
	w.Deposit(25)
	if w.Balance != 175 {
		msg := fmt.Sprintf("After Deposit(50) and Deposit(25) on a wallet with 100, the balance is %d", w.Balance)
		if w.Balance == 100 {
			msg += ": the method changed a copy of the wallet. Use a pointer receiver."
		}
		report("deposit", false, msg, 175, w.Balance)
		return
	}
	p := &Wallet{}
	p.Deposit(10)
	if p.Balance != 10 {
		report("deposit", false, fmt.Sprintf("Deposit through a *Wallet left the balance at %d", p.Balance), 10, p.Balance)
		return
	}
	report("deposit", true, "Fixed: a pointer receiver changes the caller's wallet instead of a copy.", nil, nil)
}

func TestLabboxCheckSwap(t *testing.T) {
	defer guard("swap")
	a, b := 1, 2
	Swap(&a, &b)
	if a != 2 || b != 1 {
		report("swap", false, fmt.Sprintf("After Swap(&a, &b) with a=1, b=2: a=%d, b=%d", a, b), "a=2 b=1", fmt.Sprintf("a=%d b=%d", a, b))
		return
	}
	x := 5
	Swap(&x, &x)
	if x != 5 {
		report("swap", false, fmt.Sprintf("Swap(&x, &x) changed x to %d", x), 5, x)
		return
	}
	report("swap", true, "Correct: you swapped the values the pointers point to.", nil, nil)
}
