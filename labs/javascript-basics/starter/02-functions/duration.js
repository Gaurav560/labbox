// Chapter 2: two small functions, and what happens when you forget an argument.
function minutesOf(seconds) {
  return Math.floor(seconds / 60);
}

function describe(title, seconds) {
  return `${title} (${minutesOf(seconds)} min)`;
}

console.log(describe("Monsoon Drive", 245));
console.log(minutesOf(59));
console.log(describe("Neon Lanes"));
