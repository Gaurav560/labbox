// Chapter 11: array methods and arrow functions.

function passing(marks) {
  // TODO (task passing): the marks of 40 or more, in their order
  return marks;
}

function sortByLength(words) {
  // TODO (task sort_by_length): shortest first, ties alphabetical, without changing words
  return words;
}

if (require.main === module) {
  console.log(passing([72, 30, 90, 40, 39]));
  console.log(sortByLength(["banana", "fig", "apple", "kiwi", "date"]));
}

module.exports = { passing, sortByLength };
