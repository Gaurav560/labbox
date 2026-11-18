// Ravi's Tapri ordering bot helpers. Run the examples with: node bot.js

// TODO (task parse_quantity): "2" -> 2. Anything that is not a whole number from 1 to 20 -> 0.
function parseQuantity(text) {
  return text + 0;
}

// TODO (task same_items): true when both arrays hold the same items in the same order.
function sameItems(a, b) {
  return a === b;
}

// TODO (task make_counter): makeTokenCounter("T") gives a function returning "T1", then "T2", ...
// Every counter counts on its own.
function makeTokenCounter(prefix) {
  return () => prefix + 1;
}

// TODO (task fetch_all): resolve to the list of prices, in the same order as items.
// fetchPrice(item) returns a promise of a number. Start them all at once.
async function fetchAllPrices(items, fetchPrice) {
  return [];
}

module.exports = { parseQuantity, sameItems, makeTokenCounter, fetchAllPrices };

if (require.main === module) {
  console.log(parseQuantity("2"), parseQuantity("two"));    // 2 0
  console.log(sameItems(["chai"], ["chai"]));              // true
  const next = makeTokenCounter("T");
  console.log(next(), next());                             // T1 T2
  const slow = (item) => new Promise((ok) => setTimeout(() => ok(item.length * 5), 100));
  fetchAllPrices(["chai", "bun"], slow).then(console.log); // [ 20, 15 ]
}
