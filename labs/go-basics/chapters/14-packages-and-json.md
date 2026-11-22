:::step{type=story title="How do Go programs talk to the rest of the world?"}
Parcel's vans need to tell the depot what they carry: a **manifest**. The depot's dashboard is written in JavaScript,
the billing system in Java, the phone app in Swift. They have nothing in common, except one thing: they all read
**JSON**, the text format of the web.

Go speaks JSON fluently, through one package in its standard library, and a tiny feature called **struct tags** that
turns `Weight` into `weight_kg` on the way out. To get there you first need to know how Go finds code in the first
place: **packages** and **modules**, the reason every file in this course starts with `package` something.

:::mission
Write `SaveManifest`, which turns a van's manifest into JSON, and `LoadManifest`, which reads one back, refusing broken
JSON.
:::
:::

:::step{type=concept title="Packages and modules"}
Every Go file belongs to a **package**: the first line says which. All the files in one folder are one package, and
they share everything.

A **module** is a whole project: a folder with a `go.mod` file at the top. Look at yours:

```bash run
cd /workspace && head -3 go.mod && cd 14-packages-and-json && go list .
```

```text
module labbox/lab

go 1.27
labbox/lab/14-packages-and-json
```

The module is called `labbox/lab`, so the package in the folder `14-packages-and-json` has the **import path**
`labbox/lab/14-packages-and-json`. That is exactly what `run.go` imports:

```go
import manifest "labbox/lab/14-packages-and-json"
```

From outside, only names that start with a **capital letter** can be used (chapter 2): `manifest.SaveManifest` works,
a lower-case `manifest.helper` would not compile. Real modules are named after where they live, like
`github.com/someone/project`, and `go get` downloads them.
:::

:::step{type=try title="A parcel becomes JSON" file="14-packages-and-json/json.go" line="11-30"}
Open `json.go`:

```go
type Parcel struct {
	ID      string `json:"id"`
	Weight  int    `json:"weight_kg"`
	City    string `json:"city,omitempty"`
	secret  string
	Fragile bool
}
```

```bash run
cd /workspace/14-packages-and-json && go run json.go
```

```text
{"id":"P-101","weight_kg":4,"Fragile":true} <nil>
{ID:P-202 Weight:9 City:Goa secret: Fragile:false} <nil>
json: cannot unmarshal number into Go struct field Parcel.id of type string
```

Read the first line closely:

- The text between backticks after a field is a **struct tag**. `json:"weight_kg"` renames `Weight` in the JSON.
- `city,omitempty` left the city out entirely, because it was empty.
- `secret` is missing: it starts with a small letter, so the `json` package is not allowed to see it.
- `Fragile` has no tag, so it keeps its Go name, capital F and all.
:::

:::step{type=concept title="JSON in, JSON out"}
Two functions do the work (`import "encoding/json"`):

```go
data, err := json.Marshal(p)        // a Go value becomes JSON bytes
err = json.Unmarshal(data, &back)   // JSON bytes fill in a Go value
```

- `Marshal` gives `[]byte`, which `string(data)` turns into text.
- `Unmarshal` needs a **pointer** (`&back`, chapter 11), because it has to change your variable.
- Unknown keys, like `colour` in line two, are ignored. Missing keys leave the zero value.
- And JSON of the wrong shape, like a number where the struct wants a string, comes back as an **error**, never a
  panic: line three.
:::

:::step{type=example title="Worked example: saving a delivery"}
```go
type Delivery struct {
	Stop    string `json:"stop"`
	Minutes int    `json:"minutes"`
}

func SaveDelivery(stop string, minutes int) ([]byte, error) {
	return json.Marshal(Delivery{Stop: stop, Minutes: minutes})
}

// SaveDelivery("MG Road", 25) gives {"stop":"MG Road","minutes":25}
```

1. Tags choose the JSON keys, in the style the other systems expect.
2. Build the struct value, then `json.Marshal` it.
3. `Marshal` already returns `([]byte, error)`, so it can be returned directly.
:::

:::step{type=task task=save_manifest title="Your turn: save a manifest"}
Open `manifest.go`. Give each field of `Manifest` a json tag, so the keys are `van`, `count` and `parcels`, then make
`SaveManifest(van, parcels)` give back the JSON of a `Manifest` for that van, with `Count` set to how many parcels there
are.

```bash run
cd /workspace/14-packages-and-json && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Guess first"}
:::question
A struct has a field `price int` (small p). What happens to it in `json.Marshal`?
:::
- [ ] It becomes `"price"`
- [x] It is left out
- [ ] A compile error
:::explain
Lower-case fields are not exported, so the `json` package cannot see them.
:::
:::

:::step{type=task task=load_manifest title="Your turn: load it back"}
In `manifest.go`, make `LoadManifest(data)` give back the parcels in a manifest's JSON:

- broken JSON returns an error (pass on the one from `json.Unmarshal`, wrapped if you like, chapter 13);
- a manifest with no `"parcels"` key at all returns an **empty slice, not nil**, and no error.

```bash run
cd /workspace/14-packages-and-json && go run run.go
```

Then press **Check**.
:::

:::step{type=predict title="Quick check (1 of 3)"}
:::question
What is the import path of the package in folder `14-packages-and-json` of module `labbox/lab`?
:::
- [ ] `14-packages-and-json`
- [x] `labbox/lab/14-packages-and-json`
- [ ] `manifest`
:::explain
Module path plus folder. `manifest` is the package's name, which you use in code after importing it.
:::
:::

:::step{type=predict title="Quick check (2 of 3)"}
:::question
Why does `json.Unmarshal(data, &m)` take `&m`?
:::
- [x] It has to fill in `m`, so it needs its address
- [ ] `&` makes it faster
:::explain
A function given a copy could not change your variable (chapter 11).
:::
:::

:::step{type=predict title="Quick check (3 of 3)"}
:::question
What does `json:"city,omitempty"` do when the city is `""`?
:::
- [ ] Writes `"city":""`
- [x] Leaves the key out
:::explain
`omitempty` skips zero values: empty strings, 0, false, nil.
:::
:::

:::step{type=deep-dive title="Go deeper: go get, the standard library and json.Decoder"}
**go get.** `go get github.com/someone/project` adds a module to `go.mod`, and `go.sum` records a checksum of every
download, so nobody can swap the code underneath you.

**A huge standard library.** HTTP servers, JSON, files, encryption, testing: all built in. Many Go programs need no
outside modules at all.

**json.Decoder.** `json.NewDecoder(resp.Body).Decode(&m)` reads JSON straight from a file or a network connection,
without loading it all first.
:::

:::step{type=recap title="What you can do now"}
You can now:

- Explain packages (a folder) and modules (`go.mod`), and import a package by its path.
- Turn structs into JSON with `json.Marshal`, and JSON into structs with `json.Unmarshal(data, &v)`.
- Choose JSON keys with struct tags, and use `omitempty`.
- Know what JSON never sees (lower-case fields), and handle broken JSON as an error.

:::photo{src="/lesson-images/go/go-14-notes.webp" alt="Handwritten notes about Go packages and JSON: a folder is a package, go.mod makes a module, import by path, capital letters are exported, json.Marshal turns a struct into JSON, and back again needs ampersand v, struct tags pick the keys, omitempty" ai="true"}
One page of notes for this chapter.
:::

Next, chapter 15: files and a command-line program, so Parcel can read real data from disk.
:::
