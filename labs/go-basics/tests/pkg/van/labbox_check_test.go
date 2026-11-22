package van

import (
	"encoding/json"
	"fmt"
	"testing"
)

// Hidden checks for chapter 6. Each test reports with @@RESULT and never fails, so every task reports.
func report(task string, passed bool, message string, expected, actual any) {
	if !passed {
		message = "Not yet: " + message
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

func TestLabboxCheckTotalWeight(t *testing.T) {
	defer guard("fix_total_weight")
	cases := []struct {
		in   []int
		want int
	}{{[]int{4, 12, 7}, 23}, {[]int{4}, 4}, {[]int{}, 0}, {[]int{30, 40}, 70}}
	for _, c := range cases {
		if got := TotalWeight(c.in); got != c.want {
			hint := ""
			if len(c.in) > 0 && got == c.want-c.in[0] {
				hint = " The first parcel is missing from the total. Where does the loop start?"
			}
			report("fix_total_weight", false, fmt.Sprintf("TotalWeight(%v) gave %d, but it should be %d.%s", c.in, got, c.want, hint), c.want, got)
			return
		}
	}
	report("fix_total_weight", true, "Found it: the loop started at position 1 and skipped the first parcel. Off-by-one bugs are everywhere, and now you can catch one.", nil, nil)
}

func TestLabboxCheckCanLoad(t *testing.T) {
	defer guard("fix_can_load")
	cases := []struct {
		count, limit int
		want         bool
	}{{9, 10, true}, {10, 10, false}, {0, 0, false}, {0, 5, true}, {12, 10, false}}
	for _, c := range cases {
		if got := CanLoad(c.count, c.limit); got != c.want {
			hint := ""
			if c.count == c.limit {
				hint = " At the limit there is no room left. Compare the symbols > and >= on the last line."
			}
			report("fix_can_load", false, fmt.Sprintf("CanLoad(%d, %d) gave %v, but it should be %v.%s", c.count, c.limit, got, c.want, hint), c.want, got)
			return
		}
	}
	report("fix_can_load", true, "Fixed: at the limit there is no room left. Boundaries (> or >=) are where bugs love to hide; printing the values made it visible.", nil, nil)
}
