// Chapter 16: Mixtape reads a playlist from a CSV file.
const fs = require("node:fs");

// TODO (task read_playlist): [{ title, seconds }] from a CSV with the header title,seconds; skip blank lines,
// rows with no title and seconds that are not a whole number. A missing file throws (readFileSync does that).
function readPlaylist(path) {
  return [];
}

if (require.main === module) {
  console.log(readPlaylist("playlist.csv"));
}

module.exports = { readPlaylist };
