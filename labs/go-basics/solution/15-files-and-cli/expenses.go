// Chapter 15: files. Run it with: go run run.go
package expenses

import (
	"encoding/csv"
	"errors"
	"fmt"
	"io"
	"math"
	"os"
	"strconv"
)

// ReadTotals reads a CSV with the header date,category,amount and returns the total per category,
// rounded to 2 decimals. Rows with a missing or bad amount are skipped.
func ReadTotals(path string) (map[string]float64, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("read totals: %w", err)
	}
	defer f.Close()
	r := csv.NewReader(f)
	r.FieldsPerRecord = -1
	totals := map[string]float64{}
	first := true
	for {
		row, err := r.Read()
		if errors.Is(err, io.EOF) {
			break
		}
		if err != nil {
			continue
		}
		if first {
			first = false
			continue
		}
		if len(row) < 3 {
			continue
		}
		amount, err := strconv.ParseFloat(row[2], 64)
		if err != nil {
			continue
		}
		totals[row[1]] += amount
	}
	for k, v := range totals {
		totals[k] = math.Round(v*100) / 100
	}
	return totals, nil
}
