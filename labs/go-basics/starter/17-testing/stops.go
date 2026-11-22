// Chapter 17: the van's next stop. stops_test.go says something is wrong here.
package eta

// NextStop is the position of the stop after index; after the last of count stops, back to the depot at 0.
func NextStop(index, count int) int {
	// TODO (task fix_next_stop): one test in stops_test.go fails. Read its message, then fix this line.
	return index + 1
}
