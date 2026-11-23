// Chapter 8: arrays.

function topN(numbers, n) {
  const copy = [...numbers];
  copy.sort((a, b) => b - a);
  return copy.slice(0, n);
}

function unique(items) {
  const out = [];
  for (const item of items) {
    if (!out.includes(item)) {
      out.push(item);
    }
  }
  return out;
}

if (require.main === module) {
  console.log(topN([72, 45, 90, 66], 2));
  console.log(unique(["jelly", "cookie", "jelly", "mint"]));
}

module.exports = { topN, unique };
