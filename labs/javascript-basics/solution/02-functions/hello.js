// Chapter 2: your first functions.

function greet(name) {
  return `Hello, ${name}!`;
}

function totalMinutes(hours, minutes) {
  return hours * 60 + minutes;
}

if (require.main === module) {
  console.log(greet("Asha"));
  console.log(totalMinutes(2, 15));
}

module.exports = { greet, totalMinutes };
