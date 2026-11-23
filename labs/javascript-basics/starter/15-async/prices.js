// Chapter 15: promises and async/await.

async function fetchAll(items, fetchPrice) {
  // TODO (task fetch_all): this works, but waits for one price before asking for the next.
  // Start every fetch at once and still return the prices in the items' order.
  const prices = [];
  for (const item of items) {
    prices.push(await fetchPrice(item));
  }
  return prices;
}

async function retry(task, times) {
  // TODO (task retry): call the async task up to times times; return the first success,
  // or throw the last error when every try fails
  return task();
}

if (require.main === module) {
  const fetchPrice = (item) => new Promise((resolve) => setTimeout(() => resolve(item.length * 5), 100));
  fetchAll(["cookie", "bun", "poha"], fetchPrice).then((prices) => console.log(prices));
}

module.exports = { fetchAll, retry };
