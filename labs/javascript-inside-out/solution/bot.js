// Ravi's Tapri ordering bot helpers. Run the examples with: node bot.js

function parseQuantity(text) {
  const n = Number(String(text).trim());
  return Number.isInteger(n) && n >= 1 && n <= 20 ? n : 0;
}

function sameItems(a, b) {
  return a.length === b.length && a.every((item, i) => item === b[i]);
}

function makeTokenCounter(prefix) {
  let count = 0;
  return () => {
    count += 1;
    return prefix + count;
  };
}

async function fetchAllPrices(items, fetchPrice) {
  return Promise.all(items.map((item) => fetchPrice(item)));
}

module.exports = { parseQuantity, sameItems, makeTokenCounter, fetchAllPrices };

if (require.main === module) {
  console.log(parseQuantity("2"), parseQuantity("two"));
  console.log(sameItems(["chai"], ["chai"]));
  const next = makeTokenCounter("T");
  console.log(next(), next());
  const slow = (item) => new Promise((ok) => setTimeout(() => ok(item.length * 5), 100));
  fetchAllPrices(["chai", "bun"], slow).then(console.log);
}
