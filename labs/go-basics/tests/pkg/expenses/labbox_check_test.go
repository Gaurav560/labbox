package expenses

import (
	"encoding/json"
	"fmt"
	"errors"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"strings"
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

const sample = "date,category,amount\n2026-03-02,food,120\n2026-03-02,travel,40.50\n\n2026-03-03,food,80\n2026-03-04,food,abc\n2026-03-04,travel,\n"

func writeTemp(t *testing.T, name, text string) string {
	p := filepath.Join(t.TempDir(), name)
	if err := os.WriteFile(p, []byte(text), 0o644); err != nil {
		panic(err)
	}
	return p
}

func TestLabboxCheckReadTotals(t *testing.T) {
	defer guard("read_totals")
	cases := []struct {
		text string
		want map[string]float64
	}{
		{sample, map[string]float64{"food": 200, "travel": 40.5}},
		{"date,category,amount\n", map[string]float64{}},
		{"date,category,amount\n2026-03-05,\"snacks, tea\",30\n2026-03-06,\"snacks, tea\",12.25\n", map[string]float64{"snacks, tea": 42.25}},
	}
	for _, c := range cases {
		got, err := ReadTotals(writeTemp(t, "e.csv", c.text))
		if err != nil || !reflect.DeepEqual(got, c.want) {
			report("read_totals", false, fmt.Sprintf("ReadTotals on a file like\n%s\nreturned %v, %v", strings.TrimSpace(c.text), got, err), c.want, got)
			return
		}
	}
	_, err := ReadTotals(filepath.Join(t.TempDir(), "missing.csv"))
	if err == nil || !errors.Is(err, fs.ErrNotExist) {
		report("read_totals", false, fmt.Sprintf("ReadTotals on a missing file returned %v: return (or wrap with %%w) the error from os.Open", err), "an error with errors.Is(err, fs.ErrNotExist)", err)
		return
	}
	report("read_totals", true, "ok", nil, nil)
}

const big = "date,category,amount\n2026-03-01,rent,18000\n2026-03-02,food,120\n2026-03-03,shopping,799\n2026-03-03,food,abc\n2026-03-04,travel,60\n2026-03-05,food,80.5\n2026-03-06,fun,350\n"

func TestLabboxCheckSummaryCli(t *testing.T) {
	defer guard("summary_cli")
	bin := filepath.Join(t.TempDir(), "summary")
	build := exec.Command("go", "build", "-o", bin, "./cmd/summary")
	build.Dir = ".."
	if out, err := build.CombinedOutput(); err != nil {
		report("summary_cli", false, "cmd/summary does not build:\n"+string(out), nil, nil)
		return
	}
	data := writeTemp(t, "big.csv", big)
	run := func(args ...string) (string, string, int) {
		cmd := exec.Command(bin, args...)
		var so, se strings.Builder
		cmd.Stdout, cmd.Stderr = &so, &se
		err := cmd.Run()
		code := 0
		if ee, ok := err.(*exec.ExitError); ok {
			code = ee.ExitCode()
		}
		return so.String(), se.String(), code
	}
	if out, _, _ := run("-top", "2", data); out != "rent: 18000.00\nshopping: 799.00\n" {
		report("summary_cli", false, fmt.Sprintf("summary -top 2 big.csv printed\n%s", out), "rent: 18000.00\nshopping: 799.00", out)
		return
	}
	if out, _, _ := run(data); out != "rent: 18000.00\nshopping: 799.00\nfun: 350.00\n" {
		report("summary_cli", false, fmt.Sprintf("Without -top it should print the top 3; it printed\n%s", out), "3 lines", out)
		return
	}
	missing := filepath.Join(t.TempDir(), "missing.csv")
	_, errOut, code := run(missing)
	if strings.Contains(errOut, "goroutine") || strings.Contains(errOut, "panic") {
		report("summary_cli", false, "A missing file should give one friendly line, not a panic:\n"+errOut, nil, nil)
		return
	}
	if !strings.Contains(errOut, "File not found: "+missing) || code != 1 {
		report("summary_cli", false, fmt.Sprintf("For a missing file: stderr should say \"File not found: %s\" and the exit code be 1; got %q and %d", missing, strings.TrimSpace(errOut), code), "exit 1", code)
		return
	}
	report("summary_cli", true, "ok", nil, nil)
}
