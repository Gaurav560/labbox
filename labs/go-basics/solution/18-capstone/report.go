// Chapter 18: the capstone, a depot report. Run it with: go run run.go
package report

import (
	"bufio"
	"math"
	"os"
	"strconv"
	"strings"
)

// Report is the month's summary of a deliveries file.
type Report struct {
	Delivered int            // how many good rows
	TotalKg   int            // their total weight
	AvgMins   float64        // their average delivery time, rounded to 1 decimal; 0 when there are none
	PerDepot  map[string]int // kilograms per depot
	BadLines  []int          // line numbers (the header is line 1) of rows that cannot be used
}

// DepotReport reads a deliveries CSV and builds the Report.
func DepotReport(path string) (Report, error) {
	f, err := os.Open(path)
	if err != nil {
		return Report{}, err
	}
	defer f.Close()

	r := Report{PerDepot: map[string]int{}, BadLines: []int{}}
	totalMins := 0
	scanner := bufio.NewScanner(f)
	line := 0
	for scanner.Scan() {
		line++
		text := strings.TrimSpace(scanner.Text())
		if line == 1 || text == "" {
			continue
		}
		parts := strings.Split(text, ",")
		if len(parts) != 4 || strings.TrimSpace(parts[1]) == "" {
			r.BadLines = append(r.BadLines, line)
			continue
		}
		kg, errKg := strconv.Atoi(strings.TrimSpace(parts[2]))
		mins, errMins := strconv.Atoi(strings.TrimSpace(parts[3]))
		if errKg != nil || errMins != nil {
			r.BadLines = append(r.BadLines, line)
			continue
		}
		r.Delivered++
		r.TotalKg += kg
		totalMins += mins
		r.PerDepot[strings.TrimSpace(parts[1])] += kg
	}
	if err := scanner.Err(); err != nil {
		return Report{}, err
	}
	if r.Delivered > 0 {
		r.AvgMins = math.Round(float64(totalMins)/float64(r.Delivered)*10) / 10
	}
	return r, nil
}

// BusiestDepot is the depot with the most kilograms; on a tie, the name that sorts first.
func BusiestDepot(r Report) string {
	best, bestKg := "", 0
	for depot, kg := range r.PerDepot {
		if kg > bestKg || (kg == bestKg && depot < best) {
			best, bestKg = depot, kg
		}
	}
	return best
}
