// Chapter 5: loops.

function sumTo(n) {
  // TODO (task sum_to): 1 + 2 + ... + n (0 when n is 0 or less)
  return 0;
}

function countVowels(text) {
  // TODO (task count_vowels): how many of a, e, i, o, u, in either case
  return 0;
}

if (require.main === module) {
  console.log(sumTo(5), sumTo(100), sumTo(0));
  console.log(countVowels("Hello World"), countVowels("rhythm"));
}

module.exports = { sumTo, countVowels };
