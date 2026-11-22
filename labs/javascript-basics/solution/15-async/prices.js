// Chapter 15: promises and async/await.

async function fetchAll(items, fetchPrice) {
  return Promise.all(items.map((item) => fetchPrice(item)));
}

async function retry(task, times) {
  let lastError;
  for (let i = 0; i < times; i++) {
    try {
      return await task();
    } catch (e) {
      lastError = e;
    }
  }
  throw lastError;
}

if (require.main === module) {
  const fetchPrice = (item) => new Promise((resolve) => setTimeout(() => resolve(item.length * 5), 100));
  fetchAll(["coffee", "bun", "poha"], fetchPrice).then((prices) => console.log(prices));
}

module.exports = { fetchAll, retry };
