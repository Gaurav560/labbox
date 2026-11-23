// Chapter 10: counting with objects, and sets.

function wordCounts(words) {
  // TODO (task word_counts): how many times each word appears, lower-cased
  return {};
}

function commonItems(a, b) {
  // TODO (task common_items): the items in both arrays, each once, sorted
  return [];
}

if (require.main === module) {
  console.log(wordCounts(["jelly", "Cookie", "JELLY", "jelly"]));
  console.log(commonItems(["toast", "cookie", "mint"], ["mint", "toast", "jelly"]));
}

module.exports = { wordCounts, commonItems };
