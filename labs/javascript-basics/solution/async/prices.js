// Chapter 12: promises and async/await.

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

module.exports = { fetchAll, retry };
