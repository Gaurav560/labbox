package slicetools

import (
	"encoding/json"
	"fmt"
	"reflect"
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

func TestLabboxCheckTopN(t *testing.T) {
	defer guard("top_n")
	marks := []int{72, 45, 90, 66}
	got := TopN(marks, 2)
	if !reflect.DeepEqual(marks, []int{72, 45, 90, 66}) {
		report("top_n", false, fmt.Sprintf("TopN changed the slice it was given: it is now %v. Sort a copy (slices.Clone).", marks), "[72 45 90 66]", marks)
		return
	}
	cases := []struct {
		in   []int
		n    int
		want []int
	}{{[]int{72, 45, 90, 66}, 2, []int{90, 72}}, {[]int{5, 1}, 5, []int{5, 1}}, {[]int{3, 1, 2}, 0, []int{}}, {[]int{}, 3, []int{}}, {[]int{4, 4, 1}, 2, []int{4, 4}}}
	_ = got
	for _, c := range cases {
		res := TopN(c.in, c.n)
		if len(res) != len(c.want) || (len(res) > 0 && !reflect.DeepEqual(res, c.want)) {
			report("top_n", false, fmt.Sprintf("TopN(%v, %d) returned %v", c.in, c.n, res), c.want, res)
			return
		}
	}
	report("top_n", true, "Well done: you sorted a copy, so the caller's slice is untouched. Shared backing arrays catch many Go developers; not you.", nil, nil)
}

func TestLabboxCheckUnique(t *testing.T) {
	defer guard("unique")
	cases := []struct{ in, want []string }{
		{[]string{"jelly", "cookie", "jelly", "mint", "cookie"}, []string{"jelly", "cookie", "mint"}},
		{[]string{"a", "a", "a"}, []string{"a"}},
		{[]string{"b", "a"}, []string{"b", "a"}},
	}
	for _, c := range cases {
		if got := Unique(c.in); !reflect.DeepEqual(got, c.want) {
			report("unique", false, fmt.Sprintf("Unique(%v) returned %v", c.in, got), c.want, got)
			return
		}
	}
	if got := Unique(nil); got == nil || len(got) != 0 {
		report("unique", false, "Unique(nil) returned nil: start the result as an empty slice ([]string{}) so callers get [] and JSON gets [], not null.", "[]string{}", "nil")
		return
	}
	report("unique", true, "Right: a map as a set, the original order kept, and an empty slice instead of nil.", nil, nil)
}
