// Chapter 6: arrays.

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

module.exports = { topN, unique };
