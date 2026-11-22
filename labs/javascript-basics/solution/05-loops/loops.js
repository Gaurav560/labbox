// Chapter 5: loops.

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

if (require.main === module) {
  console.log(sumTo(5), sumTo(100), sumTo(0));
  console.log(countVowels("Hello World"), countVowels("rhythm"));
}

module.exports = { sumTo, countVowels };
