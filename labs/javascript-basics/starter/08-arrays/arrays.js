// Chapter 8: arrays.

function topN(numbers, n) {
  // TODO (task top_n): the n biggest numbers, biggest first, without changing numbers
  return [];
}

function unique(items) {
  // TODO (task unique): each item once, in the order they first appear
  return items;
}

if (require.main === module) {
  console.log(topN([72, 45, 90, 66], 2));
  console.log(unique(["juice", "coffee", "juice", "milk"]));
}

module.exports = { topN, unique };
