// Chapter 10: errors.

function parseAge(text) {
  // TODO (task parse_age): a whole number from 0 to 150, spaces at the ends allowed;
  // throw a TypeError for text that is not a whole number, a RangeError above 150
  return Number(text);
}

function safeSum(values) {
  // TODO (task safe_sum): add the values that are numbers, collect the others in bad
  return { total: 0, bad: [] };
}

module.exports = { parseAge, safeSum };
