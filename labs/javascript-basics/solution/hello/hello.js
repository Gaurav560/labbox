// Chapter 1: your first functions.

function greet(name) {
  return `Hello, ${name}!`;
}

function totalMinutes(hours, minutes) {
  return hours * 60 + minutes;
}

module.exports = { greet, totalMinutes };
