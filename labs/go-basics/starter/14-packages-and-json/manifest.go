// Chapter 14: a van's manifest, saved and loaded as JSON. Run it with: go run run.go
package manifest

// Parcel is one parcel on the van. Its tags name the JSON keys.
type Parcel struct {
	ID     string `json:"id"`
	Weight int    `json:"weight_kg"`
	City   string `json:"city"`
}

// Manifest is what a van carries.
// TODO (task save_manifest): give each field a json tag, so the keys are "van", "count" and "parcels".
type Manifest struct {
	Van     string
	Count   int
	Parcels []Parcel
}

// TODO (task save_manifest): the JSON of a Manifest for this van, with Count set to how many parcels there are.
func SaveManifest(van string, parcels []Parcel) ([]byte, error) {
	return nil, nil
}

// TODO (task load_manifest): the parcels in the JSON. Broken JSON returns an error;
// a manifest with no "parcels" returns an empty slice, not nil.
func LoadManifest(data []byte) ([]Parcel, error) {
	return nil, nil
}
