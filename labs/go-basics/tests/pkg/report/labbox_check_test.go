package report

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// Hidden checks for chapter 18. Each test reports with @@RESULT and never fails, so every task reports.
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

func file(t *testing.T, text string) string {
	p := filepath.Join(t.TempDir(), "d.csv")
	os.WriteFile(p, []byte(text), 0o644)
	return p
}

const five = "id,depot,weight_kg,minutes\nP-1,Pune,4,30\nP-2,,3,20\nP-3,Goa,x,10\nP-4,Goa,6,50\n"

func TestLabboxCheckDepotReport(t *testing.T) {
	defer guard("depot_report")
	r, err := DepotReport(file(t, five))
	if err != nil {
		report("depot_report", false, fmt.Sprintf("DepotReport returned an error for a good file: %v", err), nil, nil)
		return
	}
	if r.Delivered != 2 || r.TotalKg != 10 || r.AvgMins != 40 {
		report("depot_report", false, fmt.Sprintf("for the five-line file in the lesson, the report is %d delivered, %d kg, %.1f minutes; it should be 2, 10 and 40.0. Skip the header and the bad rows.", r.Delivered, r.TotalKg, r.AvgMins), "2 10 40", fmt.Sprintf("%d %d %.1f", r.Delivered, r.TotalKg, r.AvgMins))
		return
	}
	if !reflect.DeepEqual(r.PerDepot, map[string]int{"Pune": 4, "Goa": 6}) {
		report("depot_report", false, fmt.Sprintf("PerDepot is %v, but it should be map[Goa:6 Pune:4].", r.PerDepot), "map[Goa:6 Pune:4]", r.PerDepot)
		return
	}
	if !reflect.DeepEqual(r.BadLines, []int{3, 4}) {
		report("depot_report", false, fmt.Sprintf("BadLines is %v, but it should be [3 4]: line 3 has no depot and line 4 has a weight of x. The header is line 1.", r.BadLines), "[3 4]", r.BadLines)
		return
	}
	blank, _ := DepotReport(file(t, "id,depot,weight_kg,minutes\n\nP-1,Pune,2,10\nP-2,Pune,2,\n"))
	if !reflect.DeepEqual(blank.BadLines, []int{4}) {
		report("depot_report", false, fmt.Sprintf("with a blank line before the bad row, BadLines is %v; it should be [4]. Blank lines are skipped, not reported, but they still count as lines.", blank.BadLines), "[4]", blank.BadLines)
		return
	}
	empty, err := DepotReport(file(t, "id,depot,weight_kg,minutes\n"))
	if err != nil || empty.Delivered != 0 || empty.AvgMins != 0 || empty.BadLines == nil || empty.PerDepot == nil {
		report("depot_report", false, fmt.Sprintf("a file with only the header should give zeros, an empty (not nil) map and slice, and no error; got %+v, %v.", empty, err), nil, nil)
		return
	}
	if _, err := DepotReport(filepath.Join(t.TempDir(), "missing.csv")); err == nil {
		report("depot_report", false, "a missing file should return an error: pass on the one from os.Open.", "an error", "nil")
		return
	}
	report("depot_report", true, "A complete report from messy data, with the right line numbers, empty values that are never nil, and a proper error for a missing file.", nil, nil)
}

func TestLabboxCheckBusiestDepot(t *testing.T) {
	defer guard("busiest_depot")
	cases := []struct {
		per  map[string]int
		want string
	}{
		{map[string]int{"Pune": 26, "Mumbai": 13, "Delhi": 9}, "Pune"},
		{map[string]int{"Pune": 7, "Goa": 7, "Agra": 3}, "Goa"},
		{map[string]int{}, ""},
	}
	for _, c := range cases {
		for i := 0; i < 20; i++ { // map order is random: try many times
			if got := BusiestDepot(Report{PerDepot: c.per}); got != c.want {
				report("busiest_depot", false, fmt.Sprintf("BusiestDepot with %v gave %q, but it should be %q. On a tie, the name that sorts first wins.", c.per, got, c.want), c.want, got)
				return
			}
		}
	}
	report("busiest_depot", true, "Fair every time, even though map order is random. You have finished Go from zero: well done.", nil, nil)
}
