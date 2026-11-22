// Chapter 10: which song was played most?
const plays = ["Neon Lanes", "Monsoon Drive", "Neon Lanes", "Neon Lanes"];

const counts = {};
for (const title of plays) {
  counts[title] = (counts[title] ?? 0) + 1;
}
console.log(counts);

const titles = new Set(plays);
console.log(titles, titles.size, titles.has("Slow Sunday"));
