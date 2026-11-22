package manifest

import (
	"encoding/json"
	"fmt"
	"reflect"
	"testing"
)

// Hidden checks for chapter 14. Each test reports with @@RESULT and never fails, so every task reports.
func report(task string, passed bool, message string, expected, actual any) {
	if !passed {
		message = "Not yet: " + message
	}
	r := map[string]any{"task": task, "passed": passed, "message": message}
	if expected != nil {
		r["expected"], r["actual"] = fmt.Sprint(expected), fmt.Sprint(actual)
	}
	b, _ := json.Marshal(r)
	fmt.Println("@@RESULT " + string(b))
}

func guard(task string) {
	if p := recover(); p != nil {
		report(task, false, fmt.Sprintf("your code panicked: %v", p), nil, nil)
	}
}

func TestLabboxCheckSaveManifest(t *testing.T) {
	defer guard("save_manifest")
	parcels := []Parcel{{ID: "P-1", Weight: 4, City: "Pune"}, {ID: "P-2", Weight: 9, City: "Goa"}}
	data, err := SaveManifest("Van 7", parcels)
	if err != nil {
		report("save_manifest", false, fmt.Sprintf("SaveManifest returned an error: %v", err), nil, nil)
		return
	}
	var got map[string]any
	if err := json.Unmarshal(data, &got); err != nil {
		report("save_manifest", false, fmt.Sprintf("SaveManifest gave %q, which is not JSON. Use json.Marshal on a Manifest.", data), nil, nil)
		return
	}
	for _, key := range []string{"van", "count", "parcels"} {
		if _, ok := got[key]; !ok {
			report("save_manifest", false, fmt.Sprintf("the JSON has no %q key: %s. Give each Manifest field a json tag, like `json:\"van\"`.", key, data), key, string(data))
			return
		}
	}
	if got["van"] != "Van 7" || got["count"] != float64(2) {
		report("save_manifest", false, fmt.Sprintf("the JSON is %s, but van should be \"Van 7\" and count 2 (how many parcels there are).", data), nil, nil)
		return
	}
	list, _ := got["parcels"].([]any)
	if len(list) != 2 {
		report("save_manifest", false, fmt.Sprintf("the JSON should hold both parcels; it holds %d.", len(list)), 2, len(list))
		return
	}
	report("save_manifest", true, "A manifest turned into JSON with json.Marshal, and struct tags chose the keys. That is how Go servers talk to the world.", nil, nil)
}

func TestLabboxCheckLoadManifest(t *testing.T) {
	defer guard("load_manifest")
	good := []byte(`{"van":"Van 9","count":2,"parcels":[{"id":"P-1","weight_kg":4,"city":"Pune"},{"id":"P-2","weight_kg":9,"city":"Goa"}]}`)
	want := []Parcel{{ID: "P-1", Weight: 4, City: "Pune"}, {ID: "P-2", Weight: 9, City: "Goa"}}
	got, err := LoadManifest(good)
	if err != nil || !reflect.DeepEqual(got, want) {
		report("load_manifest", false, fmt.Sprintf("LoadManifest of a two-parcel manifest gave %v, %v. Unmarshal into a Manifest and give back its Parcels.", got, err), want, got)
		return
	}
	if _, err := LoadManifest([]byte(`{"van": oops}`)); err == nil {
		report("load_manifest", false, "LoadManifest of broken JSON returned no error. Pass on the error from json.Unmarshal.", "an error", "nil")
		return
	}
	empty, err := LoadManifest([]byte(`{"van":"Van 1"}`))
	if err != nil || empty == nil || len(empty) != 0 {
		report("load_manifest", false, fmt.Sprintf("a manifest with no \"parcels\" should give an empty slice and no error; got %#v, %v.", empty, err), "[]Parcel{}", empty)
		return
	}
	report("load_manifest", true, "json.Unmarshal brought the JSON back into structs, broken JSON came back as an error, and a missing list became an empty slice.", nil, nil)
}
