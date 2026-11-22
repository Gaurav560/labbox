// Chapter 14: a van's manifest, saved and loaded as JSON. Run it with: go run run.go
package manifest

import (
	"encoding/json"
	"fmt"
)

// Parcel is one parcel on the van. Its tags name the JSON keys.
type Parcel struct {
	ID     string `json:"id"`
	Weight int    `json:"weight_kg"`
	City   string `json:"city"`
}

// Manifest is what a van carries.
type Manifest struct {
	Van     string   `json:"van"`
	Count   int      `json:"count"`
	Parcels []Parcel `json:"parcels"`
}

// SaveManifest gives the JSON of the van's manifest.
func SaveManifest(van string, parcels []Parcel) ([]byte, error) {
	return json.Marshal(Manifest{Van: van, Count: len(parcels), Parcels: parcels})
}

// LoadManifest reads the parcels from a manifest's JSON.
func LoadManifest(data []byte) ([]Parcel, error) {
	var m Manifest
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, fmt.Errorf("load manifest: %w", err)
	}
	if m.Parcels == nil {
		return []Parcel{}, nil
	}
	return m.Parcels, nil
}
