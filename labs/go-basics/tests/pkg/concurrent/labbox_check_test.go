package concurrent

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strings"
	"testing"
	"time"
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

func TestLabboxCheckFetchAll(t *testing.T) {
	defer guard("fetch_all")
	items := []string{"a", "b", "c", "d", "e"}
	slow := func(s string) string { time.Sleep(200 * time.Millisecond); return strings.ToUpper(s) }
	start := time.Now()
	got := FetchAll(items, slow)
	took := time.Since(start)
	if !reflect.DeepEqual(got, []string{"A", "B", "C", "D", "E"}) {
		report("fetch_all", false, fmt.Sprintf("FetchAll returned %v: results must be in the items' order", got), "[A B C D E]", got)
		return
	}
	if took > 600*time.Millisecond {
		report("fetch_all", false, fmt.Sprintf("Five fetches of 200 ms took %v: they ran one after another. Run them at the same time with goroutines.", took.Round(time.Millisecond)), "about 200ms", took.Round(time.Millisecond))
		return
	}
	if got := FetchAll(nil, slow); len(got) != 0 {
		report("fetch_all", false, fmt.Sprintf("FetchAll(nil) returned %v", got), "[]", got)
		return
	}
	report("fetch_all", true, "Concurrent and still in order: each goroutine wrote its own slot, and a WaitGroup waited for all of them.", nil, nil)
}

func TestLabboxCheckWordCounts(t *testing.T) {
	defer guard("word_counts")
	texts := make([]string, 200)
	for i := range texts {
		texts[i] = "Go go GOPHER juice"
	}
	want := map[string]int{"go": 400, "gopher": 200, "juice": 200}
	for round := 0; round < 5; round++ {
		if got := CountWords(texts); !reflect.DeepEqual(got, want) {
			report("word_counts", false, fmt.Sprintf("CountWords over 200 texts returned %v: with many goroutines, protect the map with a sync.Mutex", got), want, got)
			return
		}
	}
	if got := CountWords(nil); got == nil || len(got) != 0 {
		report("word_counts", false, "CountWords(nil) should return an empty map, not nil", "map[]", got)
		return
	}
	report("word_counts", true, "Exactly right under 200 goroutines: the mutex kept the map safe. That is how Go servers share data between requests.", nil, nil)
}
