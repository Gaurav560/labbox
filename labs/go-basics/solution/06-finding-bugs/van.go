// Chapter 6: two quiet bugs, found and fixed.
package van

// TotalWeight is the weight of every parcel added up, in kilograms.
func TotalWeight(weights []int) int {
	total := 0
	for i := 0; i < len(weights); i++ {
		total += weights[i]
	}
	return total
}

// CanLoad says whether a van holding count parcels has room for one more, with room for limit in all.
func CanLoad(count, limit int) bool {
	room := limit - count
	return room > 0
}
