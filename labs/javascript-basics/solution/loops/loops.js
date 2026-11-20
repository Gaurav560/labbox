// Chapter 4: loops.

function sumTo(n) {
  let total = 0;
  for (let i = 1; i <= n; i++) {
    total += i;
  }
  return total;
}

function countVowels(text) {
  let count = 0;
  for (const ch of text.toLowerCase()) {
    if ("aeiou".includes(ch)) {
      count++;
    }
  }
  return count;
}

module.exports = { sumTo, countVowels };
