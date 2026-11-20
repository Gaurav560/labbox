package words

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

func TestLabboxCheckCleanName(t *testing.T) {
	defer guard("clean_name")
	cases := map[string]string{"  riya   SHARMA ": "Riya Sharma", "ARJUN": "Arjun", "   ": "", "meera\tnair": "Meera Nair", "a b": "A B"}
	for in, want := range cases {
		if got := CleanName(in); got != want {
			report("clean_name", false, fmt.Sprintf("CleanName(%q) returned %q", in, got), want, got)
			return
		}
	}
	report("clean_name", true, "Tidy: strings.Fields, a little slicing and strings.Join did it.", nil, nil)
}

func TestLabboxCheckCountWords(t *testing.T) {
	defer guard("count_words")
	cases := map[string]int{"Go is fun": 3, "  lots   of   spaces  ": 3, "": 0, "hello, world": 2, "tab\tand\nnew line": 4}
	for in, want := range cases {
		if got := CountWords(in); got != want {
			report("count_words", false, fmt.Sprintf("CountWords(%q) returned %d", in, got), want, got)
			return
		}
	}
	report("count_words", true, "Correct even with tabs and new lines: strings.Fields does the hard part.", nil, nil)
}
