// Chapter 11: array methods and arrow functions.

function passing(marks) {
  return marks.filter((m) => m >= 40);
}

function sortByLength(words) {
  return [...words].sort((a, b) => a.length - b.length || a.localeCompare(b));
}

if (require.main === module) {
  console.log(passing([72, 30, 90, 40, 39]));
  console.log(sortByLength(["banana", "fig", "apple", "kiwi", "date"]));
}

module.exports = { passing, sortByLength };
