// Chapter 17 check: runs go test on copies of the learner's code in a scratch module.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

var pass = map[string]string{
	"fix_next_stop": "Red to green: the test told you exactly what was wrong, and % wraps the route back to the depot.",
	"test_eta":      "Your table of tests passes on the real FormatETA and caught all three planted bugs. That is what good tests do.",
}

func report(task string, ok bool, message string) {
	if ok {
		message = pass[task]
	} else {
		message = "Not yet: " + message
	}
	b, _ := json.Marshal(map[string]any{"task": task, "passed": ok, "message": message})
	fmt.Println("@@RESULT " + string(b))
}

// goTest copies files into a fresh module and runs go test there: (output, passed).
func goTest(files map[string]string) (string, bool) {
	dir, _ := os.MkdirTemp("", "labbox-gotest-")
	os.WriteFile(filepath.Join(dir, "go.mod"), []byte("module checktmp\n\ngo 1.27\n"), 0o644)
	for name, src := range files {
		data, err := os.ReadFile(src)
		if err != nil {
			return "missing " + src, false
		}
		os.WriteFile(filepath.Join(dir, name), data, 0o644)
	}
	cmd := exec.Command("go", "test", "-count=1", ".")
	cmd.Dir = dir
	out, err := cmd.CombinedOutput()
	return string(out), err == nil
}

func firstFailure(out string) string {
	for _, line := range strings.Split(out, "\n") {
		line = strings.TrimSpace(line)
		if strings.Contains(line, "_test.go:") || strings.HasPrefix(line, "./") {
			return line
		}
	}
	return "see Output"
}

func main() {
	w := os.Args[1]
	here := filepath.Dir(os.Args[0])
	_ = here
	hidden := "/check/tests/gotest"

	out, ok := goTest(map[string]string{"stops.go": filepath.Join(w, "stops.go"), "next_check_test.go": filepath.Join(hidden, "next_check_test.go")})
	if ok {
		report("fix_next_stop", true, "")
	} else {
		fmt.Print(out)
		report("fix_next_stop", false, "NextStop is not right yet: "+firstFailure(out)+". After the last stop, the van goes back to the depot at 0.")
	}

	test := filepath.Join(w, "eta_test.go")
	if _, err := os.Stat(test); err != nil {
		report("test_eta", false, "17-testing/eta_test.go is missing. Your tests for FormatETA go there.")
		return
	}
	files := func(variant string) map[string]string {
		return map[string]string{"eta.go": filepath.Join(hidden, "fines", variant, "eta.go"), "eta_test.go": test, "stops.go": filepath.Join(w, "stops.go")}
	}
	if out, ok := goTest(files("good")); !ok {
		fmt.Print(out)
		report("test_eta", false, "your tests fail on the correct FormatETA, so one of them expects the wrong answer ("+firstFailure(out)+"). Work it out from the rules again.")
	} else if _, ok := goTest(files("nopad")); ok {
		report("test_eta", false, "your tests all pass even when FormatETA forgets the leading zero (65 minutes shown as 1 h 5 min). Test a time just past the hour.")
	} else if _, ok := goTest(files("nohours")); ok {
		report("test_eta", false, "your tests all pass even when hours only start at two hours (60 minutes shown as 60 min). Test exactly one hour.")
	} else if _, ok := goTest(files("negative")); ok {
		report("test_eta", false, "your tests all pass even when FormatETA quietly accepts -1 minutes. Test that a negative number returns an error.")
	} else {
		report("test_eta", true, "")
	}
}
