// Chapter 6: two quiet bugs. This code compiles, runs, and lies.
package van

// TotalWeight is the weight of every parcel added up, in kilograms.
// TODO (task fix_total_weight): one parcel is always missing from the total. Find it with fmt.Println.
func TotalWeight(weights []int) int {
	total := 0
	for i := 1; i < len(weights); i++ {
		total += weights[i]
	}
	return total
}

// CanLoad says whether a van holding count parcels has room for one more, with room for limit in all.
// TODO (task fix_can_load): a full van still says yes. Print room, then fix the comparison.
func CanLoad(count, limit int) bool {
	room := limit - count
	return room >= 0
}
