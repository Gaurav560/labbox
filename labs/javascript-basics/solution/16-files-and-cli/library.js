// Chapter 16: Mixtape reads a playlist from a CSV file.
const fs = require("node:fs");

function readPlaylist(path) {
  const lines = fs.readFileSync(path, "utf8").split("\n");
  const songs = [];
  for (const line of lines.slice(1)) {
    const [title, seconds] = line.split(",");
    if (!title || !/^\d+$/.test((seconds ?? "").trim())) {
      continue;
    }
    songs.push({ title: title.trim(), seconds: Number(seconds) });
  }
  return songs;
}

if (require.main === module) {
  console.log(readPlaylist("playlist.csv"));
}

module.exports = { readPlaylist };
