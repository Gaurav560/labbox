// Chapter 1 check: runs the learner's small programs with go run and compares what they print.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

var pass = map[string]string{
	"hello_parcel":     "Parcel said its first words: package main, func main and two fmt.Println lines. Every Go program starts like this.",
	"fix_first_errors": "Go is happy: no unused import, no unused variable. Every import and every variable now earns its place.",
}

func report(task string, ok bool, message string) {
	if !ok {
		message = "Not yet: " + message
	} else {
		message = pass[task]
	}
	b, _ := json.Marshal(map[string]any{"task": task, "passed": ok, "message": message})
	fmt.Println("@@RESULT " + string(b))
}

func run(dir, file string) (string, string, bool) {
	cmd := exec.Command("go", "run", file)
	cmd.Dir = dir
	var out, errOut strings.Builder
	cmd.Stdout, cmd.Stderr = &out, &errOut
	err := cmd.Run()
	return out.String(), errOut.String(), err == nil
}

func firstLine(s string) string {
	for _, line := range strings.Split(s, "\n") {
		line = strings.TrimSpace(line)
		if line != "" && !strings.HasPrefix(line, "#") {
			return line
		}
	}
	return "see Output"
}

func check(dir, task, file, want, emptyHint, failHint string) {
	if _, err := os.Stat(dir + "/" + file); err != nil {
		report(task, false, fmt.Sprintf("01-hello-go/%s is missing from your workspace.", file))
		return
	}
	out, errOut, ok := run(dir, file)
	switch {
	case !ok:
		fmt.Print(errOut)
		report(task, false, fmt.Sprintf("go run %s does not work yet: %s. %s", file, firstLine(errOut), failHint))
	case out == want:
		report(task, true, "")
	case strings.TrimSpace(out) == "":
		report(task, false, emptyHint)
	default:
		report(task, false, fmt.Sprintf("go run %s printed %q, but it should print %q, exactly, capitals and full stops included.", file, strings.TrimRight(out, "\n"), strings.TrimRight(want, "\n")))
	}
}

func main() {
	dir := os.Args[1]
	check(dir, "hello_parcel", "parcel.go", "Hello! I am Parcel.\nI will track your deliveries.\n",
		"go run parcel.go printed nothing yet. Add two fmt.Println lines, and import \"fmt\".", "Read the message: it names the file, line and column.")
	check(dir, "fix_first_errors", "fixme.go", "Parcel is starting...\nReady to track your deliveries.\nParcels on the van: 12\n",
		"fixme.go runs but prints nothing. Keep the three fmt.Println lines.", "Fix one error, run it again, and read the next one.")
}
