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
  console.log(wordCounts(["juice", "Coffee", "JUICE", "juice"]));
  console.log(commonItems(["toast", "coffee", "milk"], ["milk", "toast", "juice"]));
}

module.exports = { wordCounts, commonItems };
