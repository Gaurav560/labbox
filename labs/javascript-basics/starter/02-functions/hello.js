// Chapter 2: your first functions.
// Run this file with: node hello.js

function greet(name) {
  // TODO (task greet): return "Hello, <name>!", for example "Hello, Asha!"
  return "";
}

function totalMinutes(hours, minutes) {
  // TODO (task total_minutes): turn hours and minutes into minutes
  return 0;
}

if (require.main === module) {
  console.log(greet("Asha"));
  console.log(totalMinutes(2, 15));
}

module.exports = { greet, totalMinutes };
