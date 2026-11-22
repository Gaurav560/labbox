// Chapter 16: a real command-line tool. Run it with: node cli.js playlist.csv
const { readPlaylist } = require("./library.js");

// TODO (task playlist_cli): print "<n> songs, <m>:<ss> in all" and "Longest: <title>".
// No file name: print a usage line to stderr and exit with code 2.
// A missing file: print "File not found: <path>" to stderr (no stack trace) and exit with code 1.
