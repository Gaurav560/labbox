// Chapter 10: counting with objects, and sets.

function wordCounts(words) {
  const counts = {};
  for (const w of words) {
    const key = w.toLowerCase();
    counts[key] = (counts[key] ?? 0) + 1;
  }
  return counts;
}

function commonItems(a, b) {
  const inB = new Set(b);
  return [...new Set(a)].filter((x) => inB.has(x)).sort();
}

if (require.main === module) {
  console.log(wordCounts(["jelly", "Cookie", "JELLY", "jelly"]));
  console.log(commonItems(["toast", "cookie", "mint"], ["mint", "toast", "jelly"]));
}

module.exports = { wordCounts, commonItems };
