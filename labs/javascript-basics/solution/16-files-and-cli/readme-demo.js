// Chapter 16: read a whole text file, line by line.
const fs = require("node:fs");

const text = fs.readFileSync("playlist.csv", "utf8");
const lines = text.split("\n");
console.log(lines.length, "lines");
console.log(lines.slice(0, 3));
