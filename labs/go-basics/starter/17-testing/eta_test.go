// Chapter 17: tests for FormatETA. Run them with: go test
package eta

import "testing"

func TestFormatETA(t *testing.T) {
	cases := []struct {
		minutes int
		want    string
	}{
		{45, "45 min"},
		// TODO (task test_eta): more cases, so that any wrong change to FormatETA makes this test fail.
	}
	for _, c := range cases {
		got, err := FormatETA(c.minutes)
		if err != nil || got != c.want {
			t.Errorf("FormatETA(%d) = %q, %v; want %q", c.minutes, got, err, c.want)
		}
	}
}
