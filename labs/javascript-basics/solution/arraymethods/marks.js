// Chapter 9: array methods and arrow functions.

function passing(marks) {
  return marks.filter((m) => m >= 40);
}

function sortByLength(words) {
  return [...words].sort((a, b) => a.length - b.length || a.localeCompare(b));
}

module.exports = { passing, sortByLength };
