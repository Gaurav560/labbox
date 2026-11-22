// Chapter 16: a real command-line tool. Run it with: node cli.js playlist.csv
const { readPlaylist } = require("./library.js");

const path = process.argv[2];
if (!path) {
  console.error("Usage: node cli.js <playlist.csv>");
  process.exit(2);
}

let songs;
try {
  songs = readPlaylist(path);
} catch (error) {
  if (error.code !== "ENOENT") {
    throw error;
  }
  console.error(`File not found: ${path}`);
  process.exit(1);
}

const total = songs.reduce((sum, song) => sum + song.seconds, 0);
const longest = songs.reduce((best, song) => (song.seconds > best.seconds ? song : best), songs[0]);
console.log(`${songs.length} songs, ${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")} in all`);
if (longest) {
  console.log(`Longest: ${longest.title}`);
}
