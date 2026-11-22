// Chapter 11: a playlist, filtered, mapped and added up.
const songs = [
  { title: "Monsoon Drive", seconds: 245 },
  { title: "Neon Lanes", seconds: 198 },
  { title: "Slow Sunday", seconds: 312 },
];

const long = songs.filter((s) => s.seconds > 200);
console.log(long.map((s) => s.title));
console.log(songs.map((s) => s.seconds).reduce((sum, n) => sum + n, 0));
console.log(songs.find((s) => s.title.startsWith("N")));
console.log(songs.length);
