// Chapter 17: tests for FormatETA. Run them with: go test
package eta

import "testing"

func TestFormatETA(t *testing.T) {
	cases := []struct {
		minutes int
		want    string
	}{
		{45, "45 min"},
		{0, "0 min"},
		{59, "59 min"},
		{60, "1 h 00 min"},
		{65, "1 h 05 min"},
		{125, "2 h 05 min"},
	}
	for _, c := range cases {
		got, err := FormatETA(c.minutes)
		if err != nil || got != c.want {
			t.Errorf("FormatETA(%d) = %q, %v; want %q", c.minutes, got, err, c.want)
		}
	}
}

func TestFormatETARefusesNegative(t *testing.T) {
	if _, err := FormatETA(-1); err == nil {
		t.Error("FormatETA(-1) should return an error")
	}
}
