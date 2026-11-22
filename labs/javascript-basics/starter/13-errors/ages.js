// Chapter 13: errors.

function parseAge(text) {
  // TODO (task parse_age): a whole number from 0 to 150, spaces at the ends allowed;
  // throw a TypeError for text that is not a whole number, a RangeError above 150
  return Number(text);
}

function safeSum(values) {
  // TODO (task safe_sum): add the values that are numbers, collect the others in bad
  return { total: 0, bad: [] };
}

if (require.main === module) {
  console.log(parseAge(" 42 "));
  try {
    parseAge("abc");
  } catch (error) {
    console.log(error.name + ":", error.message);
  }
  console.log(safeSum(["10", "x", "2.5", ""]));
}

module.exports = { parseAge, safeSum };
