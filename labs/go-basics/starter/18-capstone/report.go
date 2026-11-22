// Chapter 18: the capstone, a depot report. Run it with: go run run.go
package report

// Report is the month's summary of a deliveries file.
type Report struct {
	Delivered int            // how many good rows
	TotalKg   int            // their total weight
	AvgMins   float64        // their average delivery time, rounded to 1 decimal; 0 when there are none
	PerDepot  map[string]int // kilograms per depot
	BadLines  []int          // line numbers (the header is line 1) of rows that cannot be used
}

// TODO (task depot_report): read the CSV at path (header id,depot,weight_kg,minutes) and build the Report.
// Skip blank lines; a row with no depot, or a weight or minutes that is not a whole number, is a bad line.
// A missing file returns the error from opening it.
func DepotReport(path string) (Report, error) {
	return Report{}, nil
}

// TODO (task busiest_depot): the depot with the most kilograms; on a tie, the name that sorts first; "" when none.
func BusiestDepot(r Report) string {
	return ""
}
